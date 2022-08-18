<script lang="ts">
  import { push } from 'svelte-spa-router'
  import otBooks from '../data/ot_books'
  import { ntBookStore, otBookStore } from '../stores/BooksStore'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import LoadingIndicator from './LoadingIndicator.svelte'

  async function getSharedResourceCodesAndNames(
    lang0Code: string,
    lang1Code: string,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
    sharedResourceCodesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_CODES_URL
  ): Promise<Array<[string, string]>> {
    const response = await fetch(
      apiRootUrl + sharedResourceCodesUrl + lang0Code + '/' + lang1Code
    )
    const sharedResourceCodes: Array<[string, string]> = await response.json()
    if (!response.ok) throw new Error(response.statusText)
    return sharedResourceCodes
  }

  async function getResourceCodesAndNames(
    langCode: string,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
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

  // Get the lang codes from the store reactively.
  $: lang0Code = $lang0NameAndCode.split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.split(',')[1]?.split(': ')[1]
  // Get the lang names from the store reactively.
  $: lang0Name = $lang0NameAndCode.split(',')[0]
  $: lang1Name = $lang1NameAndCode.split(',')[0]

  // Resolve promise for data reactively
  // The list of all old testament books from translations.json api
  let otResourceCodes: Array<[string, string]>
  // The list of all new testament books from translations.json api
  let ntResourceCodes: Array<[string, string]>
  $: {
    if (lang0Code && lang1Code) {
      getSharedResourceCodesAndNames(lang0Code, lang1Code)
        .then(resourceCodesAndNames => {
          // Filter set of all resource codes into old testament
          // resource codes.
          otResourceCodes = resourceCodesAndNames.filter(function (
            element: [string, string]
          ) {
            return otBooks.some(item => item === element[0])
          })

          // Filter set of all resource codes into new testament
          // resource codes.
          ntResourceCodes = resourceCodesAndNames.filter(function (
            element: [string, string]
          ) {
            return !otBooks.some(item => item === element[0])
          })
        })
        .catch(err => console.error(err))
    } else {
      getResourceCodesAndNames(lang0Code)
        .then(resourceCodesAndNames => {
          // Filter set of all resource codes into old testament
          // resource codes.
          otResourceCodes = resourceCodesAndNames.filter(function (
            element: [string, string]
          ) {
            return otBooks.some(item => item === element[0])
          })

          // Filter set of all resource codes into new testament
          // resource codes.
          ntResourceCodes = resourceCodesAndNames.filter(function (
            element: [string, string]
          ) {
            return !otBooks.some(item => item === element[0])
          })
        })
        .catch(err => console.error(err))
    }
  }

  // Maintain the checkbox states reactively
  let otResourceCodesCheckboxStates: Array<boolean> = []
  $: {
    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (otResourceCodes) {
      for (const [idx, resourceCodeAndName] of otResourceCodes.entries()) {
        if ($ntBookStore && resourceCodeAndName) {
          otResourceCodesCheckboxStates[idx] = $otBookStore.some(
            item => item[0] === resourceCodeAndName[0]
          )
        } else {
          otResourceCodesCheckboxStates[idx] = false
        }
      }
    }
  }

  // Maintain the checkbox states reactively
  let ntResourceCodesCheckboxStates: Array<boolean> = []
  $: {
    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (ntResourceCodes) {
      for (const [idx, resourceCodeAndName] of ntResourceCodes.entries()) {
        if ($otBookStore && resourceCodeAndName) {
          ntResourceCodesCheckboxStates[idx] = $ntBookStore.some(
            item => item[0] === resourceCodeAndName[0]
          )
        } else {
          ntResourceCodesCheckboxStates[idx] = false
        }
      }
    }
  }

  const resetBooks = () => {
    otBookStore.set([])
    ntBookStore.set([])
  }

  function submitBooks() {
    push('#/')
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

  // Keep track of how many books are currently stored reactively.
  let nonEmptyOtBooks: boolean
  $: nonEmptyOtBooks = $otBookStore.every(item => item.length > 0)

  let nonEmptyNtBooks: boolean
  $: nonEmptyNtBooks = $ntBookStore.every(item => item.length > 0)

  let bookCount: number
  $: {
    if (nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCount = $otBookStore.length + $ntBookStore.length
    } else if (nonEmptyOtBooks && !nonEmptyNtBooks) {
      bookCount = $otBookStore.length
    } else if (!nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCount = $ntBookStore.length
    } else {
      bookCount = 0
    }
  }
</script>

{#if $lang0NameAndCode || $lang1NameAndCode}
  <div>
    {#if !(otResourceCodes && otResourceCodesCheckboxStates) || !(ntResourceCodes && ntResourceCodesCheckboxStates)}
      <LoadingIndicator />
    {:else}
      <h3 class="text-xl capitalize">
        {import.meta.env.VITE_RESOURCE_CODES_HEADER}
        {#if $lang1NameAndCode}in common{/if} for {#if $lang1NameAndCode}languages:{:else}language:{/if}
        {lang0Name}{#if $lang1NameAndCode}, {lang1Name}{/if}
      </h3>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <h3>Old Testament</h3>
          {#if otResourceCodes.length > 0}
            <div>
              <label for="select-all-old-testament"
                ><strong>Select all Old Testament</strong></label
              >
              <input
                id="select-all-old-testament"
                type="checkbox"
                class="checkbox"
                on:change={event => selectAllOtResourceCodes(event)}
              />
            </div>
          {/if}
          <ul>
            {#each otResourceCodes as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-ot-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-ot-{i}"
                  type="checkbox"
                  bind:group={$otBookStore}
                  value={resourceCodeAndName}
                  bind:checked={otResourceCodesCheckboxStates[i]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
        <div>
          <h3>New Testament</h3>
          {#if ntResourceCodes.length > 0}
            <div>
              <label for="select-all-new-testament">Select all New Testament</label>
              <input
                id="select-all-new-testament"
                type="checkbox"
                class="checkbox"
                on:change={event => selectAllNtResourceCodes(event)}
              />
            </div>
          {/if}
          <ul>
            {#each ntResourceCodes as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-nt-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-nt-{i}"
                  type="checkbox"
                  bind:group={$ntBookStore}
                  value={resourceCodeAndName}
                  bind:checked={ntResourceCodesCheckboxStates[i]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  </div>
{/if}

{#if bookCount > 0}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={submitBooks} class="btn"
      >Add ({bookCount}) Books</button
    >
  </div>

  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetBooks} class="btn">Reset books</button>
  </div>
{/if}
