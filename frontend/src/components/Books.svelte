<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  import otBooks from '../data/ot_books'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  // import {
  //   // getSharedResourceCodes
  //   // SHARED_RESOURCE_CODES
  // } from '../lib/requests'
  import { bookStore } from '../stores/BooksStore'
  import { push } from 'svelte-spa-router'

  // open-close state
  let show = false

  // The list of all old testament books from translations.json api
  let allSharedOtResourceCodes: Array<string>
  // The list of all new testament books from translations.json api
  let allSharedNtResourceCodes: Array<string>
  // The list of selected old testament resource codes by checkbox
  let sharedOtResourceCodes: Array<string> = []
  // The list of selected new testament resource codes by checkbox
  let sharedNtResourceCodes: Array<string> = []

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

    // Filter set of all resource codes into old and new testament
    // resource codes respectively.
    allSharedOtResourceCodes = json.filter(function (element: string) {
      return otBooks.includes(element[0])
    })
    allSharedNtResourceCodes = json.filter(function (element: string) {
      return !otBooks.includes(element[0])
    })
    return <string[]>json
  }

  function handleRemove(book: string) {
    bookStore.remove(book)

    // guard to close popup when there are no more messages
    if ($bookStore.length === 0) {
      show = false
    }
  }

  const resetBooks = () => {
    bookStore.clear()
    sharedOtResourceCodes = []
    sharedNtResourceCodes = []
    // close popup
    show = false
  }

  function submitBooks() {
    for (let book of sharedOtResourceCodes) {
      // console.log('add book: ' + book)
      bookStore.add(book)
    }
    for (let book of sharedNtResourceCodes) {
      // console.log('add book: ' + book)
      bookStore.add(book)
    }
    push('#/')
  }

  // function onCheckBook(event: Event) {
  //   // TODO
  //   if (event.target.checked) {

  //   }
  // }

  // https://proseandconst.xyz/blog/select-all-set/
  function selectAllOtResourceCodes(event: Event) {
    // https://stackoverflow.com/questions/66965210/property-checked-does-not-exist-on-type-eventtarget-ts2339-angular
    if ((<HTMLInputElement>event.target).checked) {
      sharedOtResourceCodes = allSharedOtResourceCodes
    } else {
      // unchecking select all checkbox means to deselect all old
      // testament checkboxes
      sharedOtResourceCodes = []
    }
    console.log('sharedOtResourceCodes: ' + sharedOtResourceCodes)
    // FIXME Is this really needed?
    // Trigger svelte to re-render component
    sharedOtResourceCodes = sharedOtResourceCodes
  }

  // https://proseandconst.xyz/blog/select-all-set/
  function selectAllNtResourceCodes(event: Event) {
    // https://stackoverflow.com/questions/66965210/property-checked-does-not-exist-on-type-eventtarget-ts2339-angular
    if ((<HTMLInputElement>event.target).checked) {
      sharedNtResourceCodes = allSharedNtResourceCodes
    } else {
      // unchecking select all checkbox means to deselect all new
      // testament checkboxes
      sharedNtResourceCodes = []
    }
    console.log('sharedNtResourceCodes: ' + sharedNtResourceCodes)
    console.log('typeof sharedNtResourceCodes[0]: ' + typeof sharedNtResourceCodes[0])
    // FIXME Is this really needed?
    // Trigger svelte to re-render component
    sharedNtResourceCodes = sharedNtResourceCodes
  }

  // Reactively get the lang code part of the lang name and code store
  $: lang0Code = $lang0NameAndCode.toString().split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.toString().split(',')[1]?.split(': ')[1]
  // Reactively get the lang name part of the lang name and code store
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
                checked={sharedOtResourceCodes.length === allSharedOtResourceCodes.length}
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
                  bind:group={sharedOtResourceCodes}
                  value={resourceCodeAndName[0]}
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
                checked={sharedNtResourceCodes.length === allSharedNtResourceCodes.length}
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
                  bind:group={sharedNtResourceCodes}
                  value={resourceCodeAndName[0]}
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

{#if sharedOtResourceCodes.length !== 0 || sharedNtResourceCodes.length !== 0}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={submitBooks} class="btn"
      >Add ({sharedOtResourceCodes.length + sharedNtResourceCodes.length}) Books</button
    >
  </div>

  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetBooks} class="btn">Reset books</button>
  </div>
{/if}
