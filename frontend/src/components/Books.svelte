<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  import otBooks from '../data/ot_books'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import { otBookStore, ntBookStore } from '../stores/BooksStore'
  import { push } from 'svelte-spa-router'

  // The list of all old testament books from translations.json api
  let allSharedOtResourceCodes: Array<string>
  // The list of all new testament books from translations.json api
  let allSharedNtResourceCodes: Array<string>

  let allSharedOtBooksAndCheckboxStates: Array<[string, boolean]> = []
  let allSharedNtBooksAndCheckboxStates: Array<[string, boolean]> = []

  export async function getSharedResourceCodes(
    lang0Code: string,
    lang1Code: string,
    api_root_url = <string>import.meta.env.VITE_BACKEND_API_URL,
    shared_resource_codes_url = <string>import.meta.env.VITE_SHARED_RESOURCE_CODES_URL
  ): Promise<string[]> {
    const response = await fetch(
      api_root_url + shared_resource_codes_url + lang0Code + '/' + lang1Code
    )
    const json = await response.json()
    if (!response.ok) throw new Error(response.statusText)

    // Filter set of all resource codes into old testament
    // resource codes.
    allSharedOtResourceCodes = json.filter(function (element: string) {
      return otBooks.includes(element[0])
    })
    // allSharedOtResourceCodes = allSharedOtResourceCodes

    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (allSharedOtResourceCodes) {
      for (const [idx, resourceCodeAndName] of allSharedOtResourceCodes.entries()) {
        if ($ntBookStore && resourceCodeAndName) {
          // TODO I'd like to find a better way of comparing than
          // using toString() which is a hack.
          allSharedOtBooksAndCheckboxStates[idx] = [
            resourceCodeAndName,
            $otBookStore.toString().includes(resourceCodeAndName.toString())
          ]
        } else {
          allSharedOtBooksAndCheckboxStates[idx] = [resourceCodeAndName, false]
        }
      }
    }

    // Filter set of all resource codes into new testament
    // resource codes.
    allSharedNtResourceCodes = json.filter(function (element: string) {
      return !otBooks.includes(element[0])
    })
    // allSharedNtResourceCodes = allSharedNtResourceCodes

    // Build up collection of tuples consisting of each
    // resourceCodeAndName and whether it already exists in the store.
    if (allSharedNtResourceCodes) {
      for (const [idx, resourceCodeAndName] of allSharedNtResourceCodes.entries()) {
        if ($otBookStore && resourceCodeAndName) {
          // TODO I'd like to find a better way of comparing than
          // using toString() which is a hack.
          allSharedNtBooksAndCheckboxStates[idx] = [
            resourceCodeAndName,
            $ntBookStore.toString().includes(resourceCodeAndName.toString())
          ]
        } else {
          allSharedNtBooksAndCheckboxStates[idx] = [resourceCodeAndName, false]
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
      otBookStore.set(allSharedOtResourceCodes)
    } else {
      otBookStore.set([])
    }
    // TODO Is this necessary?
    $otBookStore = $otBookStore
  }

  function selectAllNtResourceCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      ntBookStore.set(allSharedNtResourceCodes)
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
          {#if allSharedOtResourceCodes.length > 0}
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
            {#each allSharedOtResourceCodes as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-ot-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-ot-{i}"
                  type="checkbox"
                  bind:group={$otBookStore}
                  value={resourceCodeAndName}
                  bind:checked={allSharedOtBooksAndCheckboxStates[i][1]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
        <div>
          <h3>New Testament</h3>
          {#if allSharedNtResourceCodes.length > 0}
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
            {#each allSharedNtResourceCodes as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-nt-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-nt-{i}"
                  type="checkbox"
                  bind:group={$ntBookStore}
                  value={resourceCodeAndName}
                  bind:checked={allSharedNtBooksAndCheckboxStates[i][1]}
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
