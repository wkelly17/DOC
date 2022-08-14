<script lang="ts">
  import { push } from 'svelte-spa-router'
  import otBooks from '../data/ot_books'
  import { ntBookStore, otBookStore } from '../stores/BooksStore'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import LoadingIndicator from './LoadingIndicator.svelte'

  // The list of all old testament books from translations.json api
  let otResourceCodes: Array<string>
  // The list of all new testament books from translations.json api
  let ntResourceCodes: Array<string>

  let otResrouceCodesCheckboxStates: Array<boolean> = []
  let ntResourceCodesCheckboxStates: Array<boolean> = []

  export async function getSharedResourceCodes(
    lang0Code: string,
    lang1Code: string,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
    sharedResourceCodesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_CODES_URL
  ): Promise<string[]> {
    const response = await fetch(
      apiRootUrl + sharedResourceCodesUrl + lang0Code + '/' + lang1Code
    )
    const json = await response.json()
    if (!response.ok) throw new Error(response.statusText)

    // Filter set of all resource codes into old testament
    // resource codes.
    otResourceCodes = json.filter(function (element: string) {
      return otBooks.includes(element[0])
    })
    // otResourceCodes = otResourceCodes

    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (otResourceCodes) {
      for (const [idx, resourceCodeAndName] of otResourceCodes.entries()) {
        if ($ntBookStore && resourceCodeAndName) {
          // TODO I'd like to find a better way of comparing than
          // using toString().
          otResrouceCodesCheckboxStates[idx] = otBookStore
            .toString()
            .includes(resourceCodeAndName.toString())
        } else {
          otResrouceCodesCheckboxStates[idx] = false
        }
      }
    }

    // Filter set of all resource codes into new testament
    // resource codes.
    ntResourceCodes = json.filter(function (element: string) {
      return !otBooks.includes(element[0])
    })
    // ntResourceCodes = ntResourceCodes

    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (ntResourceCodes) {
      for (const [idx, resourceCodeAndName] of ntResourceCodes.entries()) {
        if ($otBookStore && resourceCodeAndName) {
          // TODO I'd like to find a better way of comparing than
          // using toString().
          ntResourceCodesCheckboxStates[idx] = ntBookStore
            .toString()
            .includes(resourceCodeAndName.toString())
        } else {
          ntResourceCodesCheckboxStates[idx] = false
        }
      }
    }
    return <string[]>json
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
    // TODO Is this necessary?
    $otBookStore = $otBookStore
  }

  function selectAllNtResourceCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      ntBookStore.set(ntResourceCodes)
    } else {
      ntBookStore.set([])
    }
    // TODO Is this necessary?
    $ntBookStore = $ntBookStore
  }

  // Get the lang codes from the store reactively.
  $: lang0Code = $lang0NameAndCode.toString().split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.toString().split(',')[1]?.split(': ')[1]
  // Get the lang names from the store reactively.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[0]
</script>

{#if $lang0NameAndCode && $lang1NameAndCode}
  <div>
    {#await getSharedResourceCodes(lang0Code, lang1Code)}
      <LoadingIndicator />
    {:then data}
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
                  bind:checked={otResrouceCodesCheckboxStates[i]}
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
    {:catch error}
      <p class="error">{error.message}</p>
    {/await}
  </div>
{/if}

{#if $otBookStore.length !== 0 || $ntBookStore.length !== 0}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={submitBooks} class="btn"
      >Add ({$otBookStore.length + $ntBookStore.length}) Books</button
    >
  </div>

  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetBooks} class="btn">Reset books</button>
  </div>
{/if}
