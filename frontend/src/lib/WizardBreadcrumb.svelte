<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import { langCodesStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import {
    getResourceTypeLangCode,
    resetStores,
    langRegExp,
    bookRegExp,
    resourceTypeRegExp,
    settingsRegExp
  } from '$lib/utils'
  import { resetValuesStore } from '$lib/stores/NotificationStore'
  import MobileBreadcrumb from '$lib/MobileBreadcrumb.svelte'
  import DesktopBreadcrumb from '$lib/DesktopBreadcrumb.svelte'

  function submitLanguages() {
    // If books store or resource types store are not empty, then we
    // should reset them when we change the languages.
    if ($bookCountStore > 0 || $resourceTypesCountStore > 0) {
      $resetValuesStore = true
    }
    // resetStores('books')
    // resetStores('resource_types')
    // resetStores('settings')
    // resetStores('notifications')
    goto('/books')
  }

  function submitBooks() {
    // If resource types store is not empty, then we
    // should reset it when we change books.
    if ($resourceTypesCountStore > 0) {
      $resetValuesStore = true
    }
    // resetStores('resource_types')
    // resetStores('settings')
    // resetStores('notifications')
    goto('/resource_types')
  }

  function submitResourceTypes() {
    // resetStores('settings')
    // resetStores('notifications')
    goto('/settings')
  }

  // Turn off and on breadcrumb number circles
  let turnLangStepOn: boolean = false
  let turnBookStepOn: boolean = false
  let turnResourceTypeStepOn: boolean = false
  let turnSettingsStepOn: boolean = false
  // Title and label for breadcrumb for mobile (mobile = anything
  // under sm size according to our use of tailwindcss)
  let title: string = 'Languages'
  let stepLabel: string = '1 of 4'
  $: {
    if (langRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      title = 'Languages'
      stepLabel = '1 of 4'
    } else if (bookRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = false
      turnSettingsStepOn = false
      title = 'Books'
      stepLabel = '2 of 4'
    } else if (resourceTypeRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = true
      turnSettingsStepOn = false
      title = 'Resource types'
      stepLabel = '3 of 4'
    } else if (settingsRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = true
      turnSettingsStepOn = true
      title = 'Review'
      stepLabel = '4 of 4'
    }
  }

  let numLang0ResourceTypes = 0
  let numLang1ResourceTypes = 0
  $: {
    numLang0ResourceTypes = $resourceTypesStore.filter(
      (item) => $langCodesStore[0] !== getResourceTypeLangCode(item)
    ).length
    numLang1ResourceTypes = $resourceTypesStore.filter(
      (item) => $langCodesStore[1] !== getResourceTypeLangCode(item)
    ).length
  }
</script>

<!-- wizard breadcrumb -->
<div class="border border-[#E5E8EB] p-4">
  <!-- if isMobile -->
  <MobileBreadcrumb
    {title}
    {stepLabel}
    {turnLangStepOn}
    {turnBookStepOn}
    {turnResourceTypeStepOn}
    {turnSettingsStepOn}
    {submitLanguages}
    {submitBooks}
    {submitResourceTypes}
    {numLang0ResourceTypes}
    {numLang1ResourceTypes}
  />
  <!-- else -->
  <DesktopBreadcrumb
    {turnLangStepOn}
    {turnBookStepOn}
    {turnResourceTypeStepOn}
    {turnSettingsStepOn}
    {submitLanguages}
    {submitBooks}
    {submitResourceTypes}
    {numLang0ResourceTypes}
    {numLang1ResourceTypes}
  />
  <!-- end if -->
</div>

<style lang="postcss">
  * :global(.next-button) {
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
  * :global(.next-button:hover) {
    background: linear-gradient(180deg, #0765ec 0%, #0149c8 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
</style>
