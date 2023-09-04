<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import otBooks from '../../data/ot_books'
  import { ntBookStore, otBookStore, bookCountStore } from '../../stores/v2_release/BooksStore'
  import {
    lang0CodeStore,
    lang1CodeStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { getApiRootUrl } from '../../lib/utils'

  async function getSharedResourceCodesAndNames(
    lang0Code: string,
    lang1Code: string,
    apiRootUrl = getApiRootUrl(),
    sharedResourceCodesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_CODES_URL
  ): Promise<Array<[string, string]>> {
    const response = await fetch(
      `${apiRootUrl}${sharedResourceCodesUrl}${lang0Code}/${lang1Code}`
    )
    const sharedResourceCodes: Array<[string, string]> = await response.json()
    if (!response.ok) throw new Error(response.statusText)
    return sharedResourceCodes
  }

  async function getResourceCodesAndNames(
    langCode: string,
    apiRootUrl = getApiRootUrl(),
    resourceCodesUrl = <string>import.meta.env.VITE_RESOURCE_CODES_URL
  ): Promise<Array<[string, string]>> {
    const response = await fetch(`${apiRootUrl}${resourceCodesUrl}${langCode}`)
    const resourceCodesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return resourceCodesAndNames
  }

  // Resolve promise for data reactively
  // The list of all old testament books from translations.json api
  let otResourceCodes: Array<string>
  // The list of all new testament books from translations.json api
  let ntResourceCodes: Array<string>
  if ($langCountStore > 1) {
    getSharedResourceCodesAndNames($lang0CodeStore, $lang1CodeStore)
      .then(resourceCodesAndNames => {
        // Filter set of all resource codes into old testament
        // resource codes.
        otResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If otBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any otBookStore elements that are not in otResourceCodes.
        if ($otBookStore.length > 0) {
          otBookStore.set($otBookStore.filter(item => {
            return otResourceCodes.some(element => element === item)
          }))
        }

        // Filter set of all resource codes into new testament
        // resource codes.
        ntResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return !otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)


        // If ntBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any ntBookStore elements that are not in ntResourceCodes.
        if ($ntBookStore.length > 0) {
          ntBookStore.set($ntBookStore.filter(item => {
            return ntResourceCodes.some(element => element === item)
          }))
        }
      })
      .catch(err => console.error(err))
  } else {
    getResourceCodesAndNames($lang0CodeStore)
      .then(resourceCodesAndNames => {
        // Filter set of all resource codes into old testament
        // resource codes.
        otResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If otBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any otBookStore elements that are not in otResourceCodes.
        if ($otBookStore.length > 0) {
          otBookStore.set($otBookStore.filter(item => {
            return otResourceCodes.some(element => element === item)
          }))
        }

        // Filter set of all resource codes into new testament
        // resource codes.
        ntResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return !otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If ntBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any ntBookStore elements that are not in ntResourceCodes.
        if ($ntBookStore.length > 0) {
          ntBookStore.set($ntBookStore.filter(item => {
            return ntResourceCodes.some(element => element === item)
          }))
        }
      })
      .catch(err => console.error(err))
  }


  function selectAllOtResourceCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      otBookStore.set(otResourceCodes)
    } else {
      otBookStore.set([])
    }
  }

  function selectAllNtResourceCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      ntBookStore.set(ntResourceCodes)
    } else {
      ntBookStore.set([])
    }
  }

  // Derive and set the count of books for use here and in other
  // pages.
  let nonEmptyOtBooks: boolean
  $: nonEmptyOtBooks = $otBookStore.every(item => item.length > 0)

  let nonEmptyNtBooks: boolean
  $: nonEmptyNtBooks = $ntBookStore.every(item => item.length > 0)

  $: {
    if (nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCountStore.set($otBookStore.length + $ntBookStore.length)
    } else if (nonEmptyOtBooks && !nonEmptyNtBooks) {
      bookCountStore.set($otBookStore.length)
    } else if (!nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCountStore.set($ntBookStore.length)
    } else {
      bookCountStore.set(0)
    }
  }

  let otSearchTerm = ''
  let filteredOtResourceCodes: Array<string> = []
  $: {
    if (otResourceCodes) {
      filteredOtResourceCodes = otResourceCodes.filter(item =>
        item.split(', ')[1].toLowerCase().includes(otSearchTerm.toLowerCase())
      )
    }
  }
  let ntSearchTerm = ''
  let filteredNtResourceCodes: Array<string> = []
  $: {
    if (ntResourceCodes) {
      filteredNtResourceCodes = ntResourceCodes.filter(item =>
        item.split(', ')[1].toLowerCase().includes(ntSearchTerm.toLowerCase())
      )
    }
  }

  // let showNoBooksInCommonMessage = false
  let showOldTestament = false

</script>


<WizardBreadcrumb />


<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal
               leading-[48px]">Choose books</h3>

    <!-- search and buttons -->
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !otResourceCodes || !ntResourceCodes}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showOldTestament}
            <label>
            <input
              id="filter-ot-books"
              bind:value={otSearchTerm}
              placeholder="Filter OT books"
              class="input input-bordered bg-white w-full max-w-xs"
              />
            </label>
            <div class="flex ml-2" role="group">
              <button class="rounded-l-md w-36 h-10 bg-[#015ad9]
                             text-white capitalize font-medium
                             leading-tight border-x-2 border-t-2
                             border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                      on:click={() => (showOldTestament = true)}>
                Old Testament
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-white text-[#33445c] capitalize font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
                >
                New Testament
              </button>
            </div>
          {:else}
            <label>
              <input
                id="filter-nt-books"
                bind:value={ntSearchTerm}
                placeholder="Filter NT books"
                class="input input-bordered bg-white w-full max-w-xs"
                />
            </label>
            <div class="flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-white text-[#33445c]
                       capitalize font-medium leading-tight border-x-2
                       border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = true)}
                >
                Old Testament
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-[#015ad9]
                       text-white capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
                >
                New Testament
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    {#if $langCountStore > 0}

      <!-- main content -->
      <main class="flex-1 overflow-y-auto p-4">
        {#if showOldTestament}
          {#if otResourceCodes?.length > 0}
            <div class="flex items-center">
              <input
                id="select-all-old-testament"
                class="checkbox checkbox-dark-bordered"
                on:change={event => selectAllOtResourceCodes(event)}
              />
              <label for="select-all-old-testament"
                    class="text-secondary-content pl-1"
                    >Select all</label>
            </div>
          {/if}
          {#if otResourceCodes?.length > 0}
            {#each otResourceCodes as resourceCodeAndName, index}
                <div style={filteredOtResourceCodes.includes(resourceCodeAndName) ? '' : 'display: none'}
                    class="flex items-center"
                    >
                  <input
                    id="lang-resourcecode-ot-{index}"
                    type="checkbox"
                    bind:group={$otBookStore}
                    value={resourceCodeAndName}
                    class="checkbox checkbox-dark-bordered"
                    />
                  <label for="lang-resourcecode-ot-{index}"
                        class="text-secondary-content pl-1"
                        >{resourceCodeAndName.split(', ')[1]}</label
                                                                >
                </div>
            {/each}
          {/if}
        {:else}
          {#if ntResourceCodes?.length > 0}
            <div class="flex items-center">
              <input
                id="select-all-new-testament"
                type="checkbox"
                class="checkbox checkbox-dark-bordered"
                on:change={event => selectAllNtResourceCodes(event)}
              />
              <label for="select-all-new-testament"
                    class="text-secondary-content pl-1"
                    >Select all</label>
            </div>
          {/if}
          {#if ntResourceCodes?.length > 0}
            {#each ntResourceCodes as resourceCodeAndName, index}
              <div style={filteredNtResourceCodes.includes(resourceCodeAndName) ? '' : 'display: none'}
                  class="flex items-center"
                  >
                <input
                  id="lang-resourcecode-nt-{index}"
                  type="checkbox"
                  bind:group={$ntBookStore}
                  value={resourceCodeAndName}
                  class="checkbox checkbox-dark-bordered"
                  />
                <label for="lang-resourcecode-nt-{index}"
                      class="text-secondary-content pl-1"
                      >{resourceCodeAndName.split(', ')[1]}</label
                                                              >
              </div>
            {/each}
          {/if}
        {/if}
  <!-- {#if showNoBooksInCommonMessage} -->
  <!--   <div class="toast toast-center toast-middle"> -->
  <!--     <div class="alert alert-error"> -->
  <!--       <div> -->
  <!--         <span -->
  <!--           >There are no available books in common between the two languages you chose, -->
  <!--           you can try a different language combination.</span -->
  <!--         > -->
  <!--       </div> -->
  <!--     </div> -->
  <!--   </div> -->
  <!-- {/if} -->
      </main>
    {/if}
  </div>

  <WizardBasket />

</div>


<style global lang="postcss">
  #filter-ot-books, #filter-nt-books {
    text-indent: 17px;
    padding-left: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }

  * :global(.checkbox-dark-bordered) {
    border-color: #1a130b;
    border-radius: 3px;
    width: 1em;
    height: 1em;
  }
</style>
