import { chromium } from 'playwright';

const output = process.argv[2] || 'dist/profile.webp';
const profileUrl = process.env.TARGET_URL || 'https://github.com/parsa222';
const runFolder = process.env.TILE_DIR;
const maxLoads = Number(process.env.MAX_LOADS || 24);

const CALENDAR = 'table.ContributionCalendar-grid';
const README_IMAGES = '.profile-readme img';

async function openProfile(page) {
  await page.goto(profileUrl);
  await page.waitForSelector(CALENDAR);
}

async function tileLinks(page) {
  return page.$$eval(README_IMAGES, (images) => images
    .map((img) => {
      const canonical = img.getAttribute('data-canonical-src');
      if (canonical) return canonical;
      const last = img.src.split('/').pop();
      return /^[0-9a-f]+$/i.test(last) ? decodeURIComponent(last.replace(/../g, '%$&')) : img.src;
    })
    .filter((link) => link.includes('/output/')));
}

async function waitForNewReadme(page) {
  for (let load = 1; ; load++) {
    const links = await tileLinks(page);
    const stale = links.filter((link) => !link.includes(`/output/${runFolder}/`));
    if (links.length && !stale.length) {
      console.log(`new README after ${load} page load${load > 1 ? 's' : ''}`);
      return;
    }
    if (load >= maxLoads) {
      throw new Error(`README still shows ${stale.length}/${links.length} tile links ` +
        `outside output/${runFolder}/ after ${load} loads`);
    }
    await page.waitForTimeout(5000);
    await page.reload();
    await page.waitForSelector(CALENDAR);
  }
}

async function tidyPage(page) {
  await page.evaluate((calendarSelector) => {
    document.querySelectorAll('[role=banner], [role=contentinfo]').forEach((el) => el.remove());
    const table = document.querySelector(calendarSelector);
    const graph = table.closest('.js-calendar-graph');
    const available = graph.parentElement.clientWidth;
    const natural = table.getBoundingClientRect().width;
    if (natural > available) graph.style.zoom = available / natural;
  }, CALENDAR);
}

async function finishTerminalTyping(page) {
  const terminal = await page.$(`${README_IMAGES}[src*="terminal"]`);
  if (!terminal) return;

  const src = await terminal.evaluate((img) => img.currentSrc || img.src);
  const svg = await (await fetch(src)).text();
  const duration = Number(svg.match(/animation-duration:(\d+)ms/)?.[1]);
  const typedAt = Number(svg.match(/@keyframes cur\{0%,([\d.]+)%/)?.[1]);
  if (!duration || !typedAt) {
    console.log('terminal timing not found in the card: shot at a random point of its loop');
    return;
  }

  await terminal.evaluate((img, url) => {
    img.closest('picture')?.querySelectorAll('source').forEach((source) => source.remove());
    img.src = `${url}${url.includes('?') ? '&' : '?'}shot=${Date.now()}`;
    return img.decode();
  }, src);
  const wait = duration * typedAt / 100 + 300;
  await page.waitForTimeout(wait);
  console.log(`terminal restarted, shot ${Math.round(wait)} ms later ` +
    `(typing ends at ${typedAt}% of ${duration} ms)`);
}

async function countLoadedImages(page) {
  const loaded = await page.$$eval(README_IMAGES, (images) =>
    images.map((img) => img.complete && img.naturalWidth > 0));
  if (!loaded.length || loaded.includes(false)) {
    throw new Error(`README images not loaded: ${loaded.filter(Boolean).length}/${loaded.length}`);
  }
  return loaded.length;
}

const browser = await chromium.launch({ channel: 'chrome' });
try {
  const page = await browser.newPage({ viewport: { width: 800, height: 900 }, colorScheme: 'dark' });
  await openProfile(page);
  if (runFolder) await waitForNewReadme(page);
  await tidyPage(page);
  await page.waitForTimeout(6000);
  await finishTerminalTyping(page);
  const images = await countLoadedImages(page);
  const picture = await page.screenshot({ path: output, fullPage: true, quality: 90 });
  console.log(`${output}: ${picture.length} bytes, ${images} images`);
} finally {
  await browser.close();
}
