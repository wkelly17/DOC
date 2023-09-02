<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import glLangs from '../../data/gl_languages'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    glLangCodeAndNamesStore,
    nonGlLangCodeAndNamesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import { getApiRootUrl } from '../../lib/utils'

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
        // Filter set of all languages for gl languages
        glLangCodesAndNames = langCodesAndNames_.filter((element: [string, string]) => {
          return glLangs.some((item: string) => item === element[0])
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)
        // Filter set of all languages for non-gl languages
        nonGlLangCodesAndNames = langCodesAndNames_.filter((element: [string, string]) => {
          return !glLangs.some((item: string) => item === element[0])
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)
      })
      .catch(err => console.log(err)) // FIXME Trigger toast for error
  }



  const maxLanguages = 2

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

</script>

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">

  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal leading-[48px]">Pick up to 2 languages</h3>

    <!-- search and buttons -->
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !glLangCodesAndNames || glLangCodesAndNames.length === 0|| !nonGlLangCodesAndNames || nonGlLangCodesAndNames.length === 0}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showGlLanguages}
            <label id="label-for-filter-gl-langs" for="filter-gl-langs">
              <input
                id="filter-gl-langs"
                bind:value={glLangSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-[#015ad9] text-white font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = true)}
                >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-white text-[#33445C] font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = false)}
                >
                Heart
              </button>
            </div>
          {:else}
            <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
              <input
                id="filter-non-gl-langs"
                bind:value={nonGlLangSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-white text-[#33445c] font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = true)}
                >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-[#015ad9]
                       text-white font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showGlLanguages = false)}
                >
                Heart
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

  <WizardBasket />

</div>



<style global lang="postcss">
  * :global(.checkbox-dark-bordered) {
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
