import { chromium } from 'playwright';

const out = process.argv[2] || 'dist/profile.webp';
const url = process.env.TARGET_URL || 'https://github.com/parsa222';

const browser = await chromium.launch();
try {
  const page = await browser.newPage({
    viewport: { width: 800, height: 900 },
    colorScheme: 'dark',
  });

  await page.goto(url);
  await page.waitForSelector('table.ContributionCalendar-grid');

  await page.evaluate(() => {
    document.querySelectorAll('[role=banner], [role=contentinfo]').forEach((el) => el.remove());
    const table = document.querySelector('table.ContributionCalendar-grid');
    const graph = table.closest('.js-calendar-graph');
    const available = graph.parentElement.clientWidth;
    const natural = table.getBoundingClientRect().width;
    if (natural > available) graph.style.zoom = available / natural;
  });

  await page.waitForTimeout(6000);

  const decoded = await page.$$eval('.profile-readme img', (imgs) =>
    imgs.map((img) => img.complete && img.naturalWidth > 0));
  if (!decoded.length || decoded.includes(false))
    throw new Error(`README images not loaded: ${decoded.filter(Boolean).length}/${decoded.length}`);

  const image = await page.screenshot({ path: out, fullPage: true, quality: 90 });
  console.log(`${out}: ${image.length} bytes, ${decoded.length} images`);
} finally {
  await browser.close();
}
