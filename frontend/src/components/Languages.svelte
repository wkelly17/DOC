<script lang="ts">
  import { z } from 'zod'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import LeftArrow from './LeftArrow.svelte'
  import glLangs from '../data/gl_languages'
  import { push } from 'svelte-spa-router'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    glLangCodeAndNamesStore,
    nonGlLangCodeAndNamesStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import { bookCountStore, otBookStore } from '../stores/BooksStore'
  import { resourceTypesCountStore } from '../stores/ResourceTypesStore'
  import { resetValuesStore } from '../stores/NotificationStore'
  import { getApiRootUrl, resetStores } from '../lib/utils'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'

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
        item.toLowerCase().split(", ")[1].includes(glLangSearchTerm.toLowerCase())
      )
    }
  }
  // Filter the language list reactively
  let nonGlLangSearchTerm: string = ''
  let filteredNonGlLangCodeAndNames: Array<string> = []
  $: {
    if (nonGlLangCodesAndNames) {
      filteredNonGlLangCodeAndNames = nonGlLangCodesAndNames.filter((item: string) =>
        item.toLowerCase().split(", ")[1].includes(nonGlLangSearchTerm.toLowerCase())
      )
    }
  }


  let glLabel: string = 'Gateway Languages'
  $: {
    if ($glLangCodeAndNamesStore.length) {
      glLabel = `Gateway Languages (${$glLangCodeAndNamesStore.length})`
    } else {
      glLabel = 'Gateway Languages'
    }
  }
  let nonGlLabel: string = 'Heart Languages'
  $: {
    if ($nonGlLangCodeAndNamesStore.length) {
      nonGlLabel = `Heart Languages (${$nonGlLangCodeAndNamesStore.length})`
    } else {
      nonGlLabel = 'Heart Languages'
    }
  }

  // Update stores for use in this and other pages reactively
  let glLang0Code: string = ''
  let nonGlLang0Code: string = ''
  $: {
    glLang0Code = $glLangCodeAndNamesStore[0]?.split(", ")[0]
    nonGlLang0Code = $nonGlLangCodeAndNamesStore[0]?.split(", ")[0]
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
    glLang1Code = $glLangCodeAndNamesStore[1]?.split(", ")[0]
    nonGlLang1Code = $nonGlLangCodeAndNamesStore[1]?.split(", ")[0]
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
    glLang0Name = $glLangCodeAndNamesStore[0]?.split(", ")[1]
    nonGlLang0Name = $nonGlLangCodeAndNamesStore[0]?.split(", ")[1]
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
    glLang1Name = $glLangCodeAndNamesStore[1]?.split(", ")[1]
    nonGlLang1Name = $nonGlLangCodeAndNamesStore[1]?.split(", ")[1]
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

<div class="bg-white">
  <div class="bg-white flex">
    <button
      class="bg-white hover:bg-grey-100 py-2 px-4 rounded inline-flex items-center"
      on:click={() => push('#/experimental')}
    >
      <LeftArrow backLabel="Languages" />
    </button>
  </div>
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    {#if !glLangCodesAndNames || glLangCodesAndNames.length === 0||
      !nonGlLangCodesAndNames || nonGlLangCodesAndNames.length === 0}
      <ProgressIndicator />
    {:else}
      {#if showGlLanguages}
        <label id="label-for-filter-gl-langs" for="filter-gl-langs">
          <input
            id="filter-gl-langs"
            bind:value={glLangSearchTerm}
            placeholder="Filter gateway languages"
            class="input input-bordered bg-white w-full max-w-xs mb-4"
          />
        </label>
        <div class="flex items-center">
          <div class="inline-flex" role="group">
            <button
              class="rounded-l px-6 py-2.5 bg-[#feeed8]
                      text-primary-content capitalize font-medium
                      leading-tight border-x-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-[#feeee1] focus:bg-[#feeee1] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
              on:click={() => (showGlLanguages = true)}
            >
              {glLabel}
            </button>
            <button
              class="rounded-r px-6 py-2.5 bg-white text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
              on:click={() => (showGlLanguages = false)}
            >
              {nonGlLabel}
            </button>
          </div>
        </div>
      {:else}
        <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
          <input
            id="filter-non-gl-langs"
            bind:value={nonGlLangSearchTerm}
            placeholder="Filter heart languages"
            class="input input-bordered bg-white w-full max-w-xs mb-4"
          />
        </label>
        <div class="flex items-center">
          <div class="inline-flex" role="group">
            <button
                class="rounded-r px-6 py-2.5 bg-white text-primary-content capitalize font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
              on:click={() => (showGlLanguages = true)}
            >
              {glLabel}
            </button>
            <button
                class="rounded-l px-6 py-2.5 bg-[#feeed8] text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-[#feeee1] focus:bg-[#feeee1] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
              on:click={() => (showGlLanguages = false)}
            >
              {nonGlLabel}
            </button>
          </div>
        </div>
      {/if}
      <p class="text-neutral-content pl-2 mb-4">
        Please select up to 2 languages you want to add.
      </p>
      {#if showGlLanguages}
        <ul class="py-2 px-4">
          {#each glLangCodesAndNames as langCodeAndName, index}
            <li
              style={filteredGlLangCodeAndNames.includes(langCodeAndName) ? '' : 'display :none'}
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
                >{langCodeAndName.split(", ")[1]}</label
              >
            </li>
          {/each}
        </ul>
      {:else}
        <ul class="py-2 px-4">
          {#each nonGlLangCodesAndNames as langCodeAndName, index}
            <li
              style={filteredNonGlLangCodeAndNames.includes(langCodeAndName) ? '' : 'display :none'}
              class="flex items-center"
            >
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$nonGlLangCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox checkbox-dark-bordered"
              />
              <label for="lang-code-{index}" class="text-secondary-content pl-1"
                >{langCodeAndName.split(", ")[1]}</label
              >
            </li>
          {/each}
        </ul>
      {/if}
    {/if}
  </div>

  {#if $langCountStore > 0 && $langCountStore <= maxLanguages}
    <div class="text-center px-2 pt-2 pt-2 pb-8">
      <button
        on:click|preventDefault={submitLanguages}
        class="btn orange-gradient w-5/6 capitalize"
        >Add ({$langCountStore}) Languages</button
      >
    </div>
    <!-- <div class="text-center px-2 pt-2 mb-8"> -->
    <!--   <button -->
    <!--     class="btn gray-gradiant text-neutral-content w-5/6 rounded capitalize" -->
    <!--     on:click|preventDefault={() => resetLanguages()}>Reset languages</button -->
    <!--   > -->
    <!-- </div> -->
  {/if}
  {#if $langCountStore > maxLanguages}
    <div class="toast toast-center toast-middle">
      <div class="alert alert-error">
        <div>
          <span
            >You've selected more than two languages, please choose up to two languages.</span
          >
        </div>
      </div>
    </div>
  {/if}
</div>

<style global lang="postcss">
  * :global(label[id='label-for-filter-langs']) {
    position: relative;
  }

  * :global(label[id='label-for-filter-langs']:before) {
    content: '';
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    width: 20px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill-rule='evenodd'%3E%3Cpath d='M16.036 18.455l2.404-2.405 5.586 5.587-2.404 2.404zM8.5 2C12.1 2 15 4.9 15 8.5S12.1 15 8.5 15 2 12.1 2 8.5 4.9 2 8.5 2zm0-2C3.8 0 0 3.8 0 8.5S3.8 17 8.5 17 17 13.2 17 8.5 13.2 0 8.5 0zM15 16a1 1 0 1 1 2 0 1 1 0 1 1-2 0'%3E%3C/path%3E%3C/svg%3E")
      center / contain no-repeat;
  }

  * :global(input[id='filter-langs']) {
    padding: 10px 30px;
  }

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
</style>
