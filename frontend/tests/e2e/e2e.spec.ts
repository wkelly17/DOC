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
  await page.getByText('Assamese as').click()
  await page.getByText('Español (Latin American Spanish)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians gal').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Assamese Unlocked Literal Bible (ulb)').click()
  await page.getByText('Español Latino Americano ULB (ulb)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  await page.getByRole('button', { name: 'Download PDF' }).click()
})

test('test books retained in basket on back button to languages and then forward', async ({
  page
}) => {
  await page.goto('http://localhost:8001/')
  await page.goto('http://localhost:8001/#/languages')
  await page.getByText('Amharic').click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Languages').click()
  await page.getByPlaceholder('Search Languages').fill('agn')
  await page.getByLabel('Agni Bona any-x-agnibona').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /^Amharic\(am\)$/ })
    .first()
    .click()
  await page.locator('.flex-shrink-0 > div:nth-child(4)').click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /^Amharic\(am\)$/ })
    .first()
    .click()
})
