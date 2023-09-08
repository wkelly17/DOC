<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import {
    langCodesStore,
    langNamesStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import { ntBookStore, otBookStore, bookCountStore } from '../../stores/v2_release/BooksStore'
  import { getApiRootUrl, getCode, getName } from '../../lib/utils'
  import { resourceTypesStore, resourceTypesCountStore } from '../../stores/v2_release/ResourceTypesStore';

  let showGatewayLanguages = true

  async function getLangCodesNames(
    apiRootUrl: string = getApiRootUrl(),
    langCodesAndNamesUrl: string = <string>import.meta.env.VITE_LANG_CODES_NAMES_URL_V2
  ): Promise<Array<[string, string, boolean]>> {
    console.log(`apiRootUrl: ${getApiRootUrl}`)
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`)
    const langCodeNameAndTypes: Array<[string, string, boolean]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return langCodeNameAndTypes
  }

  // Resolve promise for data
  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []
  getLangCodesNames()
  .then(langCodeNameAndTypes_ => {
    // Save result for later use
    langCodeNameAndTypes = langCodeNameAndTypes_

    // Filter set of all languages for gateway languages
    gatewayCodesAndNames = langCodeNameAndTypes_.filter((element: [string, string, boolean]) => {
      return element[2]
    })
      .map(tuple => `${tuple[0]}, ${tuple[1]}`)

    // Filter set of all languages for heart languages
    heartCodesAndNames = langCodeNameAndTypes_.filter((element: [string, string, boolean]) => {
      return !element[2]
    })
      .map(tuple => `${tuple[0]}, ${tuple[1]}`)
  })
  .catch(err => console.log(err)) // FIXME Trigger toast for error


  const maxLanguages = 2

  let nonEmptyGatewayLanguages: boolean
  $: nonEmptyGatewayLanguages = $gatewayCodeAndNamesStore.every(item => item.length > 0)

  let nonEmptyHeartLanguages: boolean
  $: nonEmptyHeartLanguages = $heartCodeAndNamesStore.every(item => item.length > 0)


  $: {
    if (nonEmptyGatewayLanguages && nonEmptyHeartLanguages) {
      // Set the langCountStore
      langCountStore.set($gatewayCodeAndNamesStore.length + $heartCodeAndNamesStore.length)

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      for (let stringTuple of $heartCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      langCodesStore.set(codes)

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      for (let stringTuple of $heartCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      langNamesStore.set(names)

      // Set the resourceTypesStore
      resourceTypesStore.set($resourceTypesStore.filter(item => $langCodesStore[0] === item.split(", ")[0] || $langCodesStore[1] === item.split(", ")[0]))

      // Set the resourceTypesCountStore
      resourceTypesCountStore.set($resourceTypesStore.length)
    } else if (nonEmptyGatewayLanguages && !nonEmptyHeartLanguages) {
      // Set the langCountStore
      langCountStore.set($gatewayCodeAndNamesStore.length)

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      langCodesStore.set(codes)

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      langNamesStore.set(names)

      // Set the resourceTypesStore
      resourceTypesStore.set($resourceTypesStore.filter(item => $langCodesStore[0] === item.split(", ")[0] || $langCodesStore[1] === item.split(", ")[0]))

      // Set the resourceTypesCountStore
      resourceTypesCountStore.set($resourceTypesStore.length)
    } else if (!nonEmptyGatewayLanguages && nonEmptyHeartLanguages) {
      // Set the langCountStore
      langCountStore.set($heartCodeAndNamesStore.length)

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $heartCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      langCodesStore.set(codes)

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $heartCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      langNamesStore.set(names)

      // Set the resourceTypesStore
      resourceTypesStore.set($resourceTypesStore.filter(item => $langCodesStore[0] === item.split(", ")[0] || $langCodesStore[1] === item.split(", ")[0]))

      // Set the resourceTypesCountStore
      resourceTypesCountStore.set($resourceTypesStore.length)
    } else {
      langCountStore.set(0)
      langCodesStore.set([])
      langNamesStore.set([])
      resourceTypesStore.set([])
      resourceTypesCountStore.set(0)
      otBookStore.set([])
      ntBookStore.set([])
      bookCountStore.set(0)
    }
  }

  // Search field handling for gateway languages
  let gatewaySearchTerm: string = ''
  let filteredGatewayCodeAndNames: Array<string> = []
  $: {
    if (gatewayCodesAndNames) {
      filteredGatewayCodeAndNames = gatewayCodesAndNames.filter((item:  string) =>
        getName(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase())
      )
    }
  }

  // Search field handling for heart languages
  let heartSearchTerm: string = ''
  let filteredHeartCodeAndNames: Array<string> = []
  $: {
    if (heartCodesAndNames) {
      filteredHeartCodeAndNames = heartCodesAndNames.filter((item: string) =>
        getName(item.toLowerCase()).includes(heartSearchTerm.toLowerCase())
      )
    }
  }

</script>

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">

  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal leading-[48px]">Pick up to 2 languages</h3>

    <!-- search and buttons -->
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !langCodeNameAndTypes || langCodeNameAndTypes.length === 0}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showGatewayLanguages}
            <label id="label-for-filter-gl-langs" for="filter-gl-langs">
              <input
                id="filter-gl-langs"
                bind:value={gatewaySearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-[#015ad9] text-white font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = true)}
                >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-white text-[#33445C] font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = false)}
                >
                Heart
              </button>
            </div>
          {:else}
            <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
              <input
                id="filter-non-gl-langs"
                bind:value={heartSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-white text-[#33445c] font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = true)}
                >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-[#015ad9]
                       text-white font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = false)}
                >
                Heart
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    {#if !(!gatewayCodesAndNames || gatewayCodesAndNames.length === 0
      || !heartCodesAndNames || heartCodesAndNames.length === 0)}
      <!-- main content -->
      <main class="flex-1 overflow-y-auto p-4">
        {#if showGatewayLanguages}
          {#each gatewayCodesAndNames  as langCodeAndName, index}
            <div class="flex items-center justify-between"
                 style={filteredGatewayCodeAndNames.includes(langCodeAndName)
                 ? '' : 'display: none'}>
              <div class="flex items-center"
                  >
                <input
                  id="lang-code-{index}"
                  type="checkbox"
                  bind:group={$gatewayCodeAndNamesStore}
                  value={langCodeAndName}
                  class="checkbox checkbox-dark-bordered"
                  />
                <label for="lang-code-{index}" class="text-[#33445C] pl-1">{getName(langCodeAndName)}</label>
              </div>
              <span class="text-[#33445C]">{getCode(langCodeAndName)}</span>
            </div>
          {/each}
        {:else}
          {#each heartCodesAndNames as langCodeAndName, index}
            <div class="flex items-center justify-between"
                 style={filteredHeartCodeAndNames.includes(langCodeAndName)
                 ? '' : 'display: none'}>
              <div class="flex items-center">
                <input
                  id="lang-code-{index}"
                  type="checkbox"
                  bind:group={$heartCodeAndNamesStore}
                  value={langCodeAndName}
                  class="checkbox checkbox-dark-bordered"
                  />
                <label for="lang-code-{index}" class="text-[#33445C] pl-1"
                       >{getName(langCodeAndName)}</label>
              </div>
              <span class="text-[#33445C]">{getCode(langCodeAndName)}</span>
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
