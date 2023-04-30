<script lang="ts">
  import { push } from 'svelte-spa-router'
  import otBooks from '../data/ot_books'
  import { ntBookStore, otBookStore, bookCountStore } from '../stores/BooksStore'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import { resourceTypesCountStore } from '../stores/ResourceTypesStore'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { resetValuesStore } from '../stores/NotificationStore'
  import LeftArrow from './LeftArrow.svelte'
  import { getApiRootUrl, resetStores } from '../lib/utils'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'

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
  $: {
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

          // Filter set of all resource codes into new testament
          // resource codes.
          ntResourceCodes = resourceCodesAndNames
            .filter((element: [string, string]) => {
              return !otBooks.some(item => item === element[0])
            })
            .map(tuple => `${tuple[0]}, ${tuple[1]}`)
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

          // Filter set of all resource codes into new testament
          // resource codes.
          ntResourceCodes = resourceCodesAndNames
            .filter((element: [string, string]) => {
              return !otBooks.some(item => item === element[0])
            })
            .map(tuple => `${tuple[0]}, ${tuple[1]}`)
        })
        .catch(err => console.error(err))
    }
  }

  function resetBooks() {
    resetStores('books')
  }

  function submitBooks() {
    // If resource types store is not empty, then we
    // should reset it when we change books.
    if ($resourceTypesCountStore > 0) {
      resetValuesStore.set(true)
    }
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/experimental')
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
  let showOldTestament = true

  let headerDisplayString: string = ''
  $: {
    if ($langCountStore > 1) {
      headerDisplayString = `Available books in common for languages: ${$lang0NameStore}, ${$lang1NameStore}`
    } else {
      headerDisplayString = `Available books for language: ${$lang0NameStore}`
    }
  }

  // DEBUG
  $: console.log(`$otBookStore: ${$otBookStore}`)
  $: console.log(`$ntBookStore: ${$ntBookStore}`)
  $: console.log(`otResourceCodes: ${otResourceCodes}`)
  $: console.log(`ntResourceCodes: ${ntResourceCodes}`)
  $: {
    if (otResourceCodes) {
      console.log(
        `checked OT items: ${otResourceCodes.map(resourceCodeAndName =>
          $otBookStore.some(item => item.split(', ')[0] === resourceCodeAndName[0])
        )}`
      )
    }
  }
  $: {
    if (ntResourceCodes) {
      console.log(
        `checked NT items: ${ntResourceCodes.map(resourceCodeAndName =>
          $ntBookStore.some(item => item.split(', ')[0] === resourceCodeAndName[0])
        )}`
      )
    }
  }
  let otLabel: string = 'Old Testament'
  $: {
    if ($otBookStore.length) {
      otLabel = `Old Testament (${$otBookStore.length})`
    } else {
      otLabel = 'Old Testament'
    }
  }
  let ntLabel: string = 'New Testament'
  $: {
    if ($ntBookStore.length) {
      ntLabel = `New Testament (${$ntBookStore.length})`
    } else {
      ntLabel = 'New Testament'
    }
  }


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
      class="bg-white hover:bg-grey-100 text-grey-darkest font-bold py-2 px-4 rounded inline-flex items-center"
      on:click={() => push('#/experimental')}
    >
      <LeftArrow backLabel="Books" />
    </button>
  </div>
  {#if $langCountStore > 0}
    <div class="bg-white px-4">
      {#if !otResourceCodes || !ntResourceCodes}
        <ProgressIndicator />
      {:else}
        <h3 class="text-xl text-secondary-content capitalize">
          {headerDisplayString}
        </h3>
        {#if showOldTestament}
          <label id="label-for-filter-ot-books" for="filter-ot-books">
            <input
              id="filter-ot-books"
              bind:value={otSearchTerm}
              placeholder="Filter OT books"
              class="input input-bordered bg-white w-full max-w-xs mb-4"
            />
          </label>
          <div class="flex items-center">
            <div class="inline-flex" role="group">
              <button
                class="rounded-l px-6 py-2.5 bg-[#feeed8]
                       text-primary-content capitalize font-medium
                       leading-tight border-x-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-[#feeee1] focus:bg-[#feeee1] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = true)}
              >
                {otLabel}
              </button>
              <button
                class="rounded-r px-6 py-2.5 bg-white text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
              >
                {ntLabel}
              </button>
            </div>
          </div>
        {:else}
          <label id="label-for-filter-nt-books" for="filter-nt-books">
            <input
              id="filter-nt-books"
              bind:value={ntSearchTerm}
              placeholder="Filter NT books"
              class="input input-bordered bg-white w-full max-w-xs mb-4"
            />
          </label>
          <div class="flex items-center">
            <div class="inline-flex" role="group">
              <button
                class="rounded-r px-6 py-2.5 bg-white text-primary-content capitalize font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = true)}
              >
                {otLabel}
              </button>
              <button
                class="rounded-l px-6 py-2.5 bg-[#feeed8] text-primary-content capitalize font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#1a130b99] hover:bg-[#feeee1] focus:bg-[#feeee1] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
              >
                {ntLabel}
              </button>
            </div>
          </div>
        {/if}
        <p class="text-neutral-content mt-4">Please select the books you want to add.</p>
        {#if showOldTestament}
          <div class="w-96">
            {#if otResourceCodes.length > 0}
              <div class="flex items-center justify-between">
                <label for="select-all-old-testament" class="text-secondary-content"
                  >Select all Old Testament</label
                >
                <input
                  id="select-all-old-testament"
                  type="checkbox"
                  class="checkbox checkbox-dark-bordered"
                  on:change={event => selectAllOtResourceCodes(event)}
                />
              </div>
            {/if}
            <ul>
              {#each otResourceCodes as resourceCodeAndName, index}
                <li
                  style={filteredOtResourceCodes.includes(resourceCodeAndName)
                    ? ''
                    : 'display: none'}
                  class="flex items-center justify-between"
                >
                  <label for="lang-resourcecode-ot-{index}" class="text-secondary-content"
                    >{resourceCodeAndName.split(', ')[1]}</label
                  >
                  <input
                    id="lang-resourcecode-ot-{index}"
                    type="checkbox"
                    bind:group={$otBookStore}
                    value={resourceCodeAndName}
                    class="checkbox checkbox-dark-bordered"
                  />
                </li>
              {/each}
            </ul>
          </div>
        {:else}
          <div class="w-96">
            {#if ntResourceCodes.length > 0}
              <div class="flex items-center justify-between">
                <label for="select-all-new-testament" class="text-secondary-content"
                  >Select all New Testament</label
                >
                <input
                  id="select-all-new-testament"
                  type="checkbox"
                  class="checkbox checkbox-dark-bordered"
                  on:change={event => selectAllNtResourceCodes(event)}
                />
              </div>
            {/if}
            <ul>
              {#each ntResourceCodes as resourceCodeAndName, index}
                <li
                  style={filteredNtResourceCodes.includes(resourceCodeAndName)
                    ? ''
                    : 'display: none'}
                  class="flex items-center justify-between"
                >
                  <label for="lang-resourcecode-nt-{index}" class="text-secondary-content"
                    >{resourceCodeAndName.split(', ')[1]}</label
                  >
                  <input
                    id="lang-resourcecode-nt-{index}"
                    type="checkbox"
                    bind:group={$ntBookStore}
                    value={resourceCodeAndName}
                    class="checkbox checkbox-dark-bordered"
                  />
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      {/if}
    </div>
  {/if}

  {#if $bookCountStore > 0 && (otResourceCodes || ntResourceCodes)}
    <div class="bg-white text-center px-2 pt-6 pb-8">
      <button
        on:click|preventDefault={submitBooks}
        class="btn w-5/6 orange-gradient text-primary-content capitalize"
        >Add ({$bookCountStore}) Books</button
      >
    </div>

    <!-- <div class="text-center  px-2 pb-8 pt-2"> -->
    <!--   <button -->
    <!--     class="btn gray-gradiant text-neutral-content w-5/6 rounded capitalize" -->
    <!--     on:click|preventDefault={() => resetBooks()}>Reset Books</button -->
    <!--   > -->
    <!-- </div> -->
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
</div>

<style global lang="postcss">
  * :global(label[id='label-for-filter-ot-books']) {
    position: relative;
  }

  * :global(label[id='label-for-filter-ot-books']:before) {
    content: '';
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    width: 20px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill-rule='evenodd'%3E%3Cpath d='M16.036 18.455l2.404-2.405 5.586 5.587-2.404 2.404zM8.5 2C12.1 2 15 4.9 15 8.5S12.1 15 8.5 15 2 12.1 2 8.5 4.9 2 8.5 2zm0-2C3.8 0 0 3.8 0 8.5S3.8 17 8.5 17 17 13.2 17 8.5 13.2 0 8.5 0zM15 16a1 1 0 1 1 2 0 1 1 0 1 1-2 0'%3E%3C/path%3E%3C/svg%3E")
      center / contain no-repeat;
  }

  * :global(input[id='filter-ot-books']) {
    padding: 10px 30px;
  }

  * :global(label[id='label-for-filter-nt-books']) {
    position: relative;
  }

  * :global(label[id='label-for-filter-nt-books']:before) {
    content: '';
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    width: 20px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill-rule='evenodd'%3E%3Cpath d='M16.036 18.455l2.404-2.405 5.586 5.587-2.404 2.404zM8.5 2C12.1 2 15 4.9 15 8.5S12.1 15 8.5 15 2 12.1 2 8.5 4.9 2 8.5 2zm0-2C3.8 0 0 3.8 0 8.5S3.8 17 8.5 17 17 13.2 17 8.5 13.2 0 8.5 0zM15 16a1 1 0 1 1 2 0 1 1 0 1 1-2 0'%3E%3C/path%3E%3C/svg%3E")
      center / contain no-repeat;
  }

  * :global(input[id='filter-nt-books']) {
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
