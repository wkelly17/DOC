import { test } from '@playwright/test'

test('test v2 ui part 1', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.goto('http://localhost:8001/#/languages')
  await page.getByText('Assamese').click()
  await page.getByText('Vietnamese').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Assamese Unlocked Literal Bible (ulb)').click()
  await page.getByText('Vietnamese Unlocked Literal Bible (ulb)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  const page1Promise = page.waitForEvent('popup')
  await page.getByRole('button', { name: 'Download PDF' }).click()
  const page1 = await page1Promise
})

test('test v2 ui part 2', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.goto('http://localhost:8001/#/languages')
  await page.getByText('English').click()
  await page.getByText('français (French)').click()
  await page.locator('div:nth-child(4) > button').click()
  await page.getByText('français (French)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.locator('.flex-shrink-0 > div:nth-child(3) > button').click()
  await page.getByText('العربية (Arabic, Standard)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Old Testament' }).click()
  await page.getByLabel('Ezra').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Edit' }).nth(1).click()
  await page.getByLabel('Ezra').uncheck()
  await page.getByLabel('1 Kings').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('French Louis Segond 1910 Bible (f10)').click()
  await page.getByText('New Arabic Version (Ketab El Hayat) (nav)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Docx').click()
  await page.getByLabel('Email me a copy of my document.').check()
  await page.getByPlaceholder('Type email address here (optional)').click()
  await page.getByPlaceholder('Type email address here (optional)').fill('foo@bar.com')
  await page.getByRole('button', { name: 'Submit' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  const page1Promise = page.waitForEvent('popup')
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download Docx' }).click()
  const page1 = await page1Promise
  const download = await downloadPromise
  await page
    .getByRole('main')
    .locator('div')
    .filter({
      hasText:
        "Mix Separate How do you want to group content? Choosing 'Mix' will interleave th"
    })
    .locator('label div')
    .nth(2)
    .click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  const page2Promise = page.waitForEvent('popup')
  const download1Promise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download Docx' }).click()
  const page2 = await page2Promise
  const download1 = await download1Promise
  await page.getByRole('combobox').selectOption('blo')
  await page.getByRole('button', { name: 'Generate File' }).click()
  const page3Promise = page.waitForEvent('popup')
  const download2Promise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download Docx' }).click()
  const page3 = await page3Promise
  const download2 = await download2Promise
})
