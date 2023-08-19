<script lang="ts">
  import { z } from 'zod'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import LeftArrow from './LeftArrow.svelte'
  import glLangs from '../../data/gl_languages'
  import { push } from 'svelte-spa-router'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    glLangCodeAndNamesStore,
    nonGlLangCodeAndNamesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import { bookCountStore, otBookStore } from '../../stores/v2_release/BooksStore'
  import { resourceTypesCountStore } from '../../stores/v2_release/ResourceTypesStore'
  import { resetValuesStore } from '../../stores/v2_release/NotificationStore'
  import { getApiRootUrl, resetStores } from '../../lib/utils'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../../lib/utils'

  let showGlLanguages = true

  async function getLangCodesNames(
    apiRootUrl: string = getApiRootUrl(),
    langCodesAndNamesUrl: string = <string>import.meta.env.VITE_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string]>> {
    console.log(`apiRootUrl: ${getApiRootUrl}`)
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`)
    const langCodesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return langCodesAndNames
  }

  // Resolve promise for data
  let glLangCodesAndNames: Array<string> = []
  let nonGlLangCodesAndNames: Array<string> = []
  $: {
    getLangCodesNames()
      .then(langCodesAndNames_ => {
        // console.log(`langCodesAndNames_: ${langCodesAndNames_}`)
        // Filter set of all languages for gl languages
        glLangCodesAndNames = langCodesAndNames_.filter((element: [string, string]) => {
          return glLangs.some((item: string) => item === element[0])
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)
        // Filter set of all languages for non-gl languages
        // console.log(`glLangCodesAndNames: ${glLangCodesAndNames}`)
        nonGlLangCodesAndNames = langCodesAndNames_.filter((element: [string, string]) => {
          return !glLangs.some((item: string) => item === element[0])
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)
        // console.log(`nonGlLangCodesAndNames: ${nonGlLangCodesAndNames}`)
      })
      .catch(err => console.log(err)) // FIXME Trigger toast for error
  }

  let resourceCodesAndTypesMapSchema = z.map(
    z.string().min(1),
    z.array(z.tuple([z.string(), z.string(), z.string()]))
  )
  type ResourceCodesAndTypesMap = z.infer<typeof resourceCodesAndTypesMapSchema>

  // let resourceCodesAndTypesMap: Map<string, Array<[string, string, string]>>
  let resourceCodesAndTypesMap: ResourceCodesAndTypesMap
  $: {
    if (resourceCodesAndTypesMap) {
      console.log(`resourceCodesAndTypesMap: ${resourceCodesAndTypesMap}`)
    }
  }

  const maxLanguages = 2

  function resetLanguages() {
    resetStores('languages')
  }

  function submitLanguages() {
    // If books store or resource types store are not empty, then we
    // should reset them when we change the languages.
    if ($bookCountStore > 0 || $resourceTypesCountStore > 0) {
      resetValuesStore.set(true)
    }
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/experimental')
  }

  function uncheckLanguage(langCodeAndName: string) {
    // console.log(`About to uncheck: ${langCodeAndName}`)
    // console.log(`$glLangCodeAndNamesStore: ${$glLangCodeAndNamesStore}`)
    glLangCodeAndNamesStore.set($glLangCodeAndNamesStore.filter(item => item != langCodeAndName))
    // console.log(`After filtering $glLangCodeAndNamesStore: ${$glLangCodeAndNamesStore}`)
  }

  // Derive and set the count of books for use here and in other
  // pages.
  let nonEmptyGlLanguages: boolean
  $: nonEmptyGlLanguages = $glLangCodeAndNamesStore.every(item => item.length > 0)

  let nonEmptyNonGlLanguages: boolean
  $: nonEmptyNonGlLanguages = $nonGlLangCodeAndNamesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyGlLanguages && nonEmptyNonGlLanguages) {
      langCountStore.set($glLangCodeAndNamesStore.length + $nonGlLangCodeAndNamesStore.length)
    } else if (nonEmptyGlLanguages && !nonEmptyNonGlLanguages) {
      langCountStore.set($glLangCodeAndNamesStore.length)
    } else if (!nonEmptyGlLanguages && nonEmptyNonGlLanguages) {
      langCountStore.set($nonGlLangCodeAndNamesStore.length)
    } else {
      langCountStore.set(0)
    }
  }

  // Filter the language list reactively
  let glLangSearchTerm: string = ''
  let filteredGlLangCodeAndNames: Array<string> = []
  $: {
    if (glLangCodesAndNames) {
      filteredGlLangCodeAndNames = glLangCodesAndNames.filter((item:  string) =>
        item.toLowerCase().split(/, (.*)/s)[1].includes(glLangSearchTerm.toLowerCase())
      )
    }
  }
  // Filter the language list reactively
  let nonGlLangSearchTerm: string = ''
  let filteredNonGlLangCodeAndNames: Array<string> = []
  $: {
    if (nonGlLangCodesAndNames) {
      filteredNonGlLangCodeAndNames = nonGlLangCodesAndNames.filter((item: string) =>
        item.toLowerCase().split(/, (.*)/s)[1].includes(nonGlLangSearchTerm.toLowerCase())
      )
    }
  }


  let glLabel: string = 'Gateway Languages'
  $: {
    if ($glLangCodeAndNamesStore.length) {
      glLabel = `Gateway (${$glLangCodeAndNamesStore.length})`
    } else {
      glLabel = 'Gateway'
    }
  }
  let nonGlLabel: string = 'Heart Languages'
  $: {
    if ($nonGlLangCodeAndNamesStore.length) {
      nonGlLabel = `Heart (${$nonGlLangCodeAndNamesStore.length})`
    } else {
      nonGlLabel = 'Heart'
    }
  }

  // Update stores for use in this and other pages reactively
  let glLang0Code: string = ''
  let nonGlLang0Code: string = ''
  $: {
    glLang0Code = $glLangCodeAndNamesStore[0]?.split(/, (.*)/s)[0]
    nonGlLang0Code = $nonGlLangCodeAndNamesStore[0]?.split(/, (.*)/s)[0]
    if (glLang0Code && nonGlLang0Code) {
      lang0CodeStore.set(glLang0Code)
      lang1CodeStore.set(nonGlLang0Code)
    } else if (!glLang0Code && nonGlLang0Code) {
      lang0CodeStore.set(nonGlLang0Code)
    } else if (glLang0Code && !nonGlLang0Code) {
      lang0CodeStore.set(glLang0Code)
    }
  }
  let glLang1Code: string = ''
  let nonGlLang1Code: string = ''
  $: {
    glLang1Code = $glLangCodeAndNamesStore[1]?.split(/, (.*)/s)[0]
    nonGlLang1Code = $nonGlLangCodeAndNamesStore[1]?.split(/, (.*)/s)[0]
    if (glLang1Code && nonGlLang1Code) {
      lang0CodeStore.set(glLang1Code)
      lang1CodeStore.set(nonGlLang1Code)
    } else if (!glLang1Code && nonGlLang1Code) {
      lang1CodeStore.set(nonGlLang1Code)
    } else if (glLang1Code && !nonGlLang1Code) {
      lang1CodeStore.set(glLang1Code)
    }
  }

  let glLang0Name: string = ''
  let nonGlLang0Name: string = ''
  $: {
    glLang0Name = $glLangCodeAndNamesStore[0]?.split(/, (.*)/s)[1]
    nonGlLang0Name = $nonGlLangCodeAndNamesStore[0]?.split(/, (.*)/s)[1]
    if (glLang0Name && nonGlLang0Name) {
      lang0NameStore.set(glLang0Name)
      lang1NameStore.set(nonGlLang0Name)
    } else if (glLang0Name && !nonGlLang0Name) {
      lang0NameStore.set(glLang0Name)
    } else if (!glLang0Name && nonGlLang0Name) {
      lang0NameStore.set(nonGlLang0Name)
    }
  }
  let glLang1Name: string = ''
  let nonGlLang1Name: string = ''
  $: {
    glLang1Name = $glLangCodeAndNamesStore[1]?.split(/, (.*)/s)[1]
    nonGlLang1Name = $nonGlLangCodeAndNamesStore[1]?.split(/, (.*)/s)[1]
    if (glLang1Name && nonGlLang1Name) {
      lang0NameStore.set(glLang1Name)
      lang1NameStore.set(nonGlLang1Name)
    } else if (glLang1Name && !nonGlLang1Name) {
      lang1NameStore.set(glLang1Name)
    } else if (!glLang1Name && nonGlLang1Name) {
      lang1NameStore.set(nonGlLang1Name)
    }
  }

  $: console.log(`$langCountStore: ${$langCountStore}`)

  // For sidebar
  let open = false
  let showTopMatter: boolean = setShowTopMatter()
</script>

{#if showTopMatter}
  <Sidebar bind:open />
  <Mast bind:sidebar="{open}" />
  <Tabs />
{/if}


<!-- wizard breadcrumb -->
<div class="p-4 border border-[#E5E8EB]">
  <div class="flex items-center justify-between text-[#B3B9C2]
              leading-8 text-xl font-semibold">
    <button class="btn">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M18.0374 10.5166H7.28489L11.9825 5.69276C12.3579 5.30724 12.3579 4.6746 11.9825 4.28908C11.8934 4.19744 11.7877 4.12474 11.6712 4.07514C11.5547 4.02553 11.4299 4 11.3038 4C11.1778 4 11.0529 4.02553 10.9365 4.07514C10.82 4.12474 10.7142 4.19744 10.6252 4.28908L4.28151 10.8033C4.19227 10.8948 4.12148 11.0034 4.07317 11.123C4.02486 11.2426 4 11.3707 4 11.5002C4 11.6297 4.02486 11.7579 4.07317 11.8774C4.12148 11.997 4.19227 12.1057 4.28151 12.1971L10.6252 18.7113C10.7143 18.8029 10.8201 18.8755 10.9366 18.925C11.053 18.9745 11.1778 19 11.3038 19C11.4299 19 11.5547 18.9745 11.6711 18.925C11.7876 18.8755 11.8934 18.8029 11.9825 18.7113C12.0716 18.6198 12.1423 18.5112 12.1905 18.3916C12.2388 18.272 12.2636 18.1439 12.2636 18.0144C12.2636 17.885 12.2388 17.7569 12.1905 17.6373C12.1423 17.5177 12.0716 17.4091 11.9825 17.3175L7.28489 12.4937H18.0374C18.5668 12.4937 19 12.0488 19 11.5052C19 10.9615 18.5668 10.5166 18.0374 10.5166Z" fill="#33445C"/>
      </svg>Back
    </button>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        <div class="bg-neutral-focus text-neutral-content rounded-full
                    w-8 bg-[#015ad9]">
          <span class="text-xs text-white">1</span>
        </div>
      </div>
      <span class="ml-2">Languages</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        <div class="bg-neutral-focus text-neutral-content rounded-full
                    w-8 bg-[#B3B9C2]">
          <span class="text-xs text-white">2</span>
        </div>
      </div>
      <span class="ml-2">Books</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        <div class="bg-neutral-focus text-neutral-content rounded-full
                    w-8 bg-[#B3B9C2]">
          <span class="text-xs text-white">3</span>
        </div>
      </div>
      <span class="ml-2">Resources</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        <div class="bg-neutral-focus text-neutral-content rounded-full
                    w-8 bg-[#B3B9C2]">
          <span class="text-xs text-white">4</span>
        </div>
      </div>
      <span class="ml-2">Review</span>
    </div>
    <button class="btn">Next
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z" fill="#001533"/>
      </svg>
    </button>
  </div>
</div>

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">

  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="text-[#33445C] text-4xl font-normal leading-[48px]">Pick up to 2 Languages</h3>

    <!-- search and buttons -->
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !glLangCodesAndNames || glLangCodesAndNames.length === 0|| !nonGlLangCodesAndNames || nonGlLangCodesAndNames.length === 0}
        <ProgressIndicator />
      {:else}
        <div class="flex items-center">
          {#if showGlLanguages}
            <label id="label-for-filter-gl-langs" for="filter-gl-langs">
              <input
                id="filter-gl-langs"
                type="search"
                bind:value={glLangSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-32 h-10 bg-[#015ad9]
                       text-white capitalize font-medium
                       leading-tight border-x-1 border-t-1 border-b-1
                       border-[#1a130b99] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = true)}
                >
                {glLabel}
              </button>
              <button
                class="rounded-r-md w-32 h-10 bg-white text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = false)}
                >
                {nonGlLabel}
              </button>
            </div>
          {:else}
            <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
              <input
                id="filter-non-gl-langs"
                type="search"
                bind:value={nonGlLangSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-32 h-10 bg-white text-primary-content capitalize font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = true)}
                >
                {glLabel}
              </button>
              <button
                class="rounded-r-md w-32 h-10 bg-[#015ad9]
                       text-white  text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = false)}
                >
                {nonGlLabel}
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    {#if !(!glLangCodesAndNames || glLangCodesAndNames.length === 0|| !nonGlLangCodesAndNames || nonGlLangCodesAndNames.length === 0)}
      <!-- main content -->
      <main class="flex-1 overflow-y-auto p-4">
        {#if showGlLanguages}
          {#each glLangCodesAndNames as langCodeAndName, index}
            <div style={filteredGlLangCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
                 class="flex items-center"
                 >
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$glLangCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox checkbox-dark-bordered"
                />
              <label for="lang-code-{index}" class="text-secondary-content pl-1"
                     >{langCodeAndName.split(/, (.*)/s)[1]}</label>
            </div>
          {/each}
        {:else}
          {#each nonGlLangCodesAndNames as langCodeAndName, index}
            <div style={filteredNonGlLangCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
                 class="flex items-center">
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$nonGlLangCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox checkbox-dark-bordered"
                />
              <label for="lang-code-{index}" class="text-secondary-content pl-1"
                     >{langCodeAndName.split(/, (.*)/s)[1]}</label>
            </div>
          {/each}
        {/if}

        {#if $langCountStore > 0 && $langCountStore <= maxLanguages}
          <div class="text-center px-2 pt-2 pt-2 pb-8">
            <button
              on:click|preventDefault={submitLanguages}
              class="btn orange-gradient w-5/6 capitalize"
              >Add ({$langCountStore}) Languages</button>
          </div>
        {/if}

        {#if $langCountStore > maxLanguages}
          <div class="toast toast-center toast-middle">
            <div class="alert alert-error">
              <div>
                <span>You've selected more than two languages, please choose up to two languages.</span>
              </div>
            </div>
          </div>
        {/if}
      </main>
    {/if}
  </div>

  <!-- right sidebar -->
  <div class="flex-shrink-0 w-1/3 p-4 overflow-y-auto bg-[#f2f3f5]">
    <h1 class="pl-0 py-4 font-semibold text-xl text-[#33445C]">Your Selection</h1>
    <div class="inline-flex items-center">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z" fill="#001533"/>
      </svg>
      <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Language</h2>
    </div>
    {#if $glLangCodeAndNamesStore && $glLangCodeAndNamesStore.length > 0}
      {#each $glLangCodeAndNamesStore as langCodeAndName}
        <div class="inline-flex items-center justify-between w-full rounded-lg p-6 bg-white
                    text-[#66768B] mt-2">{langCodeAndName.split(/, (.*)/s)[1]}
          <button on:click={() => uncheckLanguage(langCodeAndName)}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
            </svg>
          </button>
        </div>
      {/each}
    {:else}
      <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768b]">Selections will appear here once a language is selected</div>
    {/if}
    <div class="inline-flex items-center">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 22C5.45 22 4.97933 21.8043 4.588 21.413C4.196 21.021 4 20.55 4 20V4C4 3.45 4.196 2.979 4.588 2.587C4.97933 2.19567 5.45 2 6 2H18C18.55 2 19.021 2.19567 19.413 2.587C19.8043 2.979 20 3.45 20 4V20C20 20.55 19.8043 21.021 19.413 21.413C19.021 21.8043 18.55 22 18 22H6ZM6 20H18V4H16V10.125C16 10.325 15.9167 10.4707 15.75 10.562C15.5833 10.654 15.4167 10.65 15.25 10.55L13.5 9.5L11.75 10.55C11.5833 10.65 11.4167 10.654 11.25 10.562C11.0833 10.4707 11 10.325 11 10.125V4H6V20ZM11 4H16H11ZM6 4H18H6Z" fill="#001533"/>
      </svg>
      <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Book</h2>
    </div>
    <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768B]">Selections will appear here once a book is selected</div>
    <div class="inline-flex items-center">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 2C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2H6ZM6 4H13V9H18V20H6V4ZM8 12V14H16V12H8ZM8 16V18H13V16H8Z" fill="#001533"/>
      </svg>
     <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Resource</h2>
    </div>
    <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768B]">Selections will appear here once a resource is selected</div>
  </div>
</div>

<!-- footer -->
<div class="bg-blue-700 p-4">
  Footer
</div>


<style global lang="postcss">
  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }

  * :global(.checkbox-dark-bordered) {
    /* --chkbg: #1a130b; */
    border-color: #1a130b;
    border-radius: 3px;
    width: 1em;
    height: 1em;
  }
  #filter-gl-langs, #filter-non-gl-langs {
    text-indent: 17px;
    padding-left: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }
  input[type="checkbox"]:checked + label {
    background: #e6eefb;
  }
</style>
