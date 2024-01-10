<script lang="ts">
  import { location } from 'svelte-spa-router'
  import { push } from 'svelte-spa-router'
  import { langCodesStore, langCountStore } from '../stores/LanguagesStore'
  import { bookCountStore } from '../stores/BooksStore'
  import {
    resourceTypesStore,
    resourceTypesCountStore
  } from '../stores/ResourceTypesStore'
  import {
    getResourceTypeLangCode,
    resetStores,
    langRegExp,
    bookRegExp,
    resourceTypeRegExp,
    settingsRegExp
  } from '../lib/utils'
  import { resetValuesStore } from '../stores/NotificationStore'
  import BackButton from './BackButton.svelte'
  import NextButton from './NextButton.svelte'

  function submitLanguages() {
    // If books store or resource types store are not empty, then we
    // should reset them when we change the languages.
    if ($bookCountStore > 0 || $resourceTypesCountStore > 0) {
      $resetValuesStore = true
    }
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/books')
  }

  function submitBooks() {
    // If resource types store is not empty, then we
    // should reset it when we change books.
    if ($resourceTypesCountStore > 0) {
      $resetValuesStore = true
    }
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/resource_types')
  }

  function submitResourceTypes() {
    resetStores('settings')
    resetStores('notifications')
    push('#/settings')
  }

  const MAX_LANGUAGES = <number>import.meta.env.VITE_MAX_LANGUAGES

  // Turn off and on breadcrumb number circles
  let turnLangStepOn: boolean = false
  let turnBookStepOn: boolean = false
  let turnResourceTypeStepOn: boolean = false
  let turnSettingsStepOn: boolean = false
  // Title and label for breadcrumb for mobile (mobile = anything
  // under sm size according to our use of tailwindcss)
  let smTitle: string = 'Languages'
  let smStepLabel: string = '1 of 4'
  $: {
    if (langRegExp.test($location)) {
      turnLangStepOn = true
      smTitle = 'Languages'
      smStepLabel = '1 of 4'
    } else if (bookRegExp.test($location)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = false
      turnSettingsStepOn = false
      smTitle = 'Books'
      smStepLabel = '2 of 4'
    } else if (resourceTypeRegExp.test($location)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = true
      turnSettingsStepOn = false
      smTitle = 'Resource types'
      smStepLabel = '3 of 4'
    } else if (settingsRegExp.test($location)) {
      turnLangStepOn = true
      turnBookStepOn = true
      turnResourceTypeStepOn = true
      turnSettingsStepOn = true
      smTitle = 'Review'
      smStepLabel = '4 of 4'
    }
  }

  let numLang0ResourceTypes = 0
  let numLang1ResourceTypes = 0
  $: {
    numLang0ResourceTypes = $resourceTypesStore.filter(
      item => $langCodesStore[0] !== getResourceTypeLangCode(item)
    ).length
    numLang1ResourceTypes = $resourceTypesStore.filter(
      item => $langCodesStore[1] !== getResourceTypeLangCode(item)
    ).length
  }
</script>

<!-- wizard breadcrumb -->
<div class="p-4 border border-[#E5E8EB]">
  <!-- {#if isMobile} -->
  <div
    class="flex sm:hidden items-center justify-between text-[#B3B9C2] leading-8 text-xl font-semibold"
  >
    <!-- mobile only page title -->
    <div>
      <h3 class="text-[#015AD9]">{smTitle}</h3>
      <h4 class="text-[#33445C]">Step {smStepLabel}</h4>
    </div>
    <div class="flex items-center">
      <!-- back button logic -->
      {#if bookRegExp.test($location)}
        <BackButton url="/languages" />
      {:else if resourceTypeRegExp.test($location)}
        <BackButton url="/books" />
      {:else if settingsRegExp.test($location)}
        <BackButton url="/resource_types" />
      {:else}
        <button
          class="flex items-center bg-white border border-[#E5E8EB]
                 text-[#33445c] py-2 px-4
                 rounded-md cursor-not-allowed"
          disabled
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M18.0374 10.5166H7.28489L11.9825 5.69276C12.3579 5.30724 12.3579 4.6746 11.9825 4.28908C11.8934 4.19744 11.7877 4.12474 11.6712 4.07514C11.5547 4.02553 11.4299 4 11.3038 4C11.1778 4 11.0529 4.02553 10.9365 4.07514C10.82 4.12474 10.7142 4.19744 10.6252 4.28908L4.28151 10.8033C4.19227 10.8948 4.12148 11.0034 4.07317 11.123C4.02486 11.2426 4 11.3707 4 11.5002C4 11.6297 4.02486 11.7579 4.07317 11.8774C4.12148 11.997 4.19227 12.1057 4.28151 12.1971L10.6252 18.7113C10.7143 18.8029 10.8201 18.8755 10.9366 18.925C11.053 18.9745 11.1778 19 11.3038 19C11.4299 19 11.5547 18.9745 11.6711 18.925C11.7876 18.8755 11.8934 18.8029 11.9825 18.7113C12.0716 18.6198 12.1423 18.5112 12.1905 18.3916C12.2388 18.272 12.2636 18.1439 12.2636 18.0144C12.2636 17.885 12.2388 17.7569 12.1905 17.6373C12.1423 17.5177 12.0716 17.4091 11.9825 17.3175L7.28489 12.4937H18.0374C18.5668 12.4937 19 12.0488 19 11.5052C19 10.9615 18.5668 10.5166 18.0374 10.5166Z"
              fill="#33445C"
            /></svg
          ><span class="hidden sm:inline">Back</span>
        </button>
      {/if}
      <!-- next button logic -->
      {#if langRegExp.test($location) && $langCountStore > 0 && $langCountStore <= MAX_LANGUAGES}
        <NextButton func={submitLanguages} />
      {:else if bookRegExp.test($location) && $bookCountStore > 0}
        <NextButton func={submitBooks} />
      {:else if resourceTypeRegExp.test($location) && (($langCountStore == 1 && $resourceTypesCountStore > 0) || ($langCountStore === 2 && numLang0ResourceTypes > 0 && numLang1ResourceTypes > 0))}
        <NextButton func={submitResourceTypes} />
      {:else}
        <button
          class="flex items-center bg-white border border-[#E5E8EB]
                 text-[#33445c] py-2 px-4 rounded-md ml-2 cursor-not-allowed"
          disabled
        >
          <span class="hidden sm:inline">Next</span>
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
              fill="#001533"
            />
          </svg>
        </button>
      {/if}
    </div>
  </div>
  <!-- {:else} -->
  <!-- desktop -->
  <div
    class="hidden sm:flex items-center justify-between text-[#B3B9C2] leading-8 text-xl font-semibold"
  >
    <!-- back button logic -->
    {#if bookRegExp.test($location)}
      <BackButton url="/languages" />
    {:else if resourceTypeRegExp.test($location)}
      <BackButton url="/books" />
    {:else if settingsRegExp.test($location)}
      <BackButton url="/resource_types" />
    {:else}
      <button
        class="flex items-center bg-white border border-[#E5E8EB]
                 text-[#33445c] py-2 px-4
                 rounded-md cursor-not-allowed"
        disabled
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18.0374 10.5166H7.28489L11.9825 5.69276C12.3579 5.30724 12.3579 4.6746 11.9825 4.28908C11.8934 4.19744 11.7877 4.12474 11.6712 4.07514C11.5547 4.02553 11.4299 4 11.3038 4C11.1778 4 11.0529 4.02553 10.9365 4.07514C10.82 4.12474 10.7142 4.19744 10.6252 4.28908L4.28151 10.8033C4.19227 10.8948 4.12148 11.0034 4.07317 11.123C4.02486 11.2426 4 11.3707 4 11.5002C4 11.6297 4.02486 11.7579 4.07317 11.8774C4.12148 11.997 4.19227 12.1057 4.28151 12.1971L10.6252 18.7113C10.7143 18.8029 10.8201 18.8755 10.9366 18.925C11.053 18.9745 11.1778 19 11.3038 19C11.4299 19 11.5547 18.9745 11.6711 18.925C11.7876 18.8755 11.8934 18.8029 11.9825 18.7113C12.0716 18.6198 12.1423 18.5112 12.1905 18.3916C12.2388 18.272 12.2636 18.1439 12.2636 18.0144C12.2636 17.885 12.2388 17.7569 12.1905 17.6373C12.1423 17.5177 12.0716 17.4091 11.9825 17.3175L7.28489 12.4937H18.0374C18.5668 12.4937 19 12.0488 19 11.5052C19 10.9615 18.5668 10.5166 18.0374 10.5166Z"
            fill="#33445C"
          /></svg
        ><span class="hidden sm:inline">Back</span>
      </button>
    {/if}
    <!-- breadcrumb link logic -->
    <div class="hidden sm:inline-flex items-center">
      <div class="avatar placeholder">
        {#if turnLangStepOn}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8"
            style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
          >
            <span class="text-xs text-white">1</span>
          </div>
        {:else}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]"
          >
            <span class="text-xs text-white">1</span>
          </div>
        {/if}
      </div>
      <span class="ml-2"><a href="#/languages">Languages</a></span>
    </div>
    <div class="hidden sm:inline-flex items-center">
      <div class="avatar placeholder">
        {#if turnBookStepOn}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8"
            style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
          >
            <span class="text-xs text-white">2</span>
          </div>
        {:else}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]"
          >
            <span class="text-xs text-white">2</span>
          </div>
        {/if}
      </div>
      {#if turnBookStepOn}
        <span class="ml-2"><a href="#/books">Books</a></span>
      {:else}
        <span class="ml-2">Books</span>
      {/if}
    </div>
    <div class="hidden sm:inline-flex items-center">
      <div class="avatar placeholder">
        {#if turnResourceTypeStepOn}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8"
            style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
          >
            <span class="text-xs text-white">3</span>
          </div>
        {:else}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]"
          >
            <span class="text-xs text-white">3</span>
          </div>
        {/if}
      </div>
      {#if turnResourceTypeStepOn}
        <span class="ml-2"><a href="#/resource_types">Resources</a></span>
      {:else}
        <span class="ml-2">Resources</span>
      {/if}
    </div>
    <div class="hidden sm:inline-flex items-center">
      <div class="avatar placeholder">
        {#if turnSettingsStepOn}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8"
            style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
          >
            <span class="text-xs text-white">4</span>
          </div>
        {:else}
          <div
            class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]"
          >
            <span class="text-xs text-white">4</span>
          </div>
        {/if}
      </div>
      <span class="ml-2">Review</span>
    </div>
    <!-- next button logic -->
    {#if langRegExp.test($location) && $langCountStore > 0 && $langCountStore <= MAX_LANGUAGES}
      <NextButton func={submitLanguages} />
    {:else if bookRegExp.test($location) && $bookCountStore > 0}
      <NextButton func={submitBooks} />
    {:else if resourceTypeRegExp.test($location) && (($langCountStore === 1 && $resourceTypesCountStore > 0) || ($langCountStore === 2 && numLang0ResourceTypes > 0 && numLang1ResourceTypes > 0))}
      <NextButton func={submitResourceTypes} />
    {:else}
      <button
        class="flex items-center bg-white border border-[#E5E8EB]
                 text-[#33445c] py-2 px-4
                 rounded-md cursor-not-allowed"
        disabled
      >
        <span class="hidden sm:inline">Next</span>
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
            fill="#001533"
          />
        </svg>
      </button>
    {/if}
  </div>

  <!-- {/if} -->
</div>

<style lang="css">
  * :global(.next-button) {
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
  * :global(.next-button:hover) {
    background: linear-gradient(180deg, #0765ec 0%, #0149c8 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
</style>
