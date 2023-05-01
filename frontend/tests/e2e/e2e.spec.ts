import { test, expect, type Page } from '@playwright/test'

test.beforeEach(async ({ page, baseURL }) => {
  console.log(`Using FRONTEND_API_URL: ${baseURL}`)
  await page.goto(baseURL!)
})

test('test pt-br, mat, mrk, ulb, tn, tq, tw, 1c', async ({ page }) => {
  await page.getByRole('link', { name: 'About' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/about')

  await page.getByRole('link', { name: 'here' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/languages')

  await page.getByLabel('Brazilian Português').check()

  await page.getByRole('button', { name: 'Add (1) Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/books')

  await page.getByRole('button', { name: 'New Testament' }).click()

  await page.getByLabel('Matthew').check()

  await page.getByLabel('Mark').check()

  await page.getByRole('button', { name: 'Add (2) Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '3. Resource types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/resource_types')

  await page.getByLabel('Translation Notes (tn)').check()

  await page.getByLabel('Translation Questions (tq)').check()

  await page.getByLabel('Translation Words (tw)').check()

  await page.getByLabel('Brazilian Portuguese Unlocked Literal Bible (ulb)').check()

  await page.getByRole('button', { name: 'Add (4) Resource Types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('link', { name: 'Settings' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/settings')

  await page.getByLabel('(Optional) Generate PDF').check()

  await page.getByRole('button', { name: 'Generate Document' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/result')

  const [page1] = await Promise.all([
    page.waitForEvent('popup'),
    page.getByRole('button', { name: 'Download PDF' }).click()
  ])
})

test('test ePub and Docx options not available when print layout is chosen, but PDF is available', async ({
  page
}) => {
  await page.getByRole('link', { name: 'About' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/about')

  await page.getByRole('link', { name: 'here' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/languages')

  await page.getByLabel('Brazilian Português').check()

  await page.getByLabel('Español (Latin American Spanish)').check()

  await page.getByRole('button', { name: 'Add (2) Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/books')

  await page.getByLabel('Genesis').check()

  await page.getByRole('button', { name: 'Add (1) Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '3. Resource types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/resource_types')

  await page.getByLabel("Select all Brazilian Português's resource types").check()

  await page
    .getByLabel(
      "Select all\n                  Español (Latin American Spanish)'s resource types"
    )
    .check()

  await page.getByRole('button', { name: 'Add (8) Resource Types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('link', { name: 'Settings' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/settings')

  await expect(page.locator('span:has-text("(Optional) Generate PDF")')).toBeVisible()
  await expect(
    page.locator('span:has-text("(Optional) Generate ePub")')
  ).not.toBeVisible()
  await expect(
    page.locator('span:has-text("(Optional) Generate Docx")')
  ).not.toBeVisible()
})

test('test assembly strategy drop down not available when print layout deselected and only one language chosen; PDF, ePub, Docx options present', async ({
  page
}) => {
  await page.getByRole('link', { name: 'About' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/about')

  await page.getByRole('link', { name: 'here' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/languages')
  await page.getByLabel('Español (Latin American Spanish)').check()
  await page.getByRole('button', { name: 'Add (1) Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')
  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/books')
  await page.getByLabel('Genesis').check()
  await page.getByRole('button', { name: 'Add (1) Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')
  await page.getByRole('button', { name: '3. Resource types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/resource_types')
  await page
    .getByLabel(
      "Select all\n                  Español (Latin American Spanish)'s resource types"
    )
    .check()
  await page.getByRole('button', { name: 'Add (4) Resource Types' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')
  await page.getByRole('link', { name: 'Settings' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/settings')
  await page
    .locator(
      'li:has-text("Print Optimization Enabling this option will remove extra whitespace") div'
    )
    .nth(3)
    .click()
  await expect(page.locator('select[name="assemblyStrategy"]')).not.toBeVisible()
  await expect(page.locator('span:has-text("(Optional) Generate PDF")')).toBeVisible()
  await expect(page.locator('span:has-text("(Optional) Generate ePub")')).toBeVisible()
  await expect(page.locator('span:has-text("(Optional) Generate Docx")')).toBeVisible()
})

test('test v1 ui', async ({ page }) => {
  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/languages')

  await page.getByLabel('Nepali').check()

  await page.getByLabel('Tagalog').check()

  await page.getByRole('button', { name: 'Add (2) Languages' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/')

  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/books')

  await page.getByRole('button', { name: 'New Testament' }).click()

  await page.getByLabel('Matthew').check()

  await page.getByLabel('Mark').check()

  await page.getByRole('button', { name: 'Add (2) Books' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/')

  await page.getByRole('button', { name: 'Generate Document' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/result')

  const [page1] = await Promise.all([
    page.waitForEvent('popup'),
    page.getByRole('button', { name: 'Download PDF' }).click()
  ])
})

test('test navigate between ui versions via links in about pages', async ({ page }) => {
  await page.getByRole('link', { name: 'About' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/about')

  await page.getByRole('link', { name: 'here' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental')

  await page.getByRole('link', { name: 'About' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/experimental/about')

  await page.getByRole('link', { name: 'here' }).click()
  await expect(page).toHaveURL('http://localhost:8001/#/')
})
