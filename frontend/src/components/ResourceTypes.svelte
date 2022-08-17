<script lang="ts">
  import { push } from 'svelte-spa-router'
  import { ntBookStore, otBookStore } from '../stores/BooksStore'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore
  } from '../stores/ResourceTypesStore'
  import LoadingIndicator from './LoadingIndicator.svelte'

  // Get the lang codes from the store reactively.
  $: lang0Code = $lang0NameAndCode.split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.split(',')[1]?.split(': ')[1]
  // Get the lang names from the store reactively.
  $: lang0Name = $lang0NameAndCode.split(',')[0]
  $: lang1Name = $lang1NameAndCode.split(',')[0]

  async function getResourceTypes(
    langCode: string,
    resourceCodeAndNames: Array<[string, string]>,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
    resourceTypesUrl = <string>import.meta.env.VITE_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string]>> {
    const url_ = `${apiRootUrl}${resourceTypesUrl}${langCode}/`
    const url = new URL(url_)
    resourceCodeAndNames.map(resourceCodeAndName =>
      url.searchParams.append('resource_codes', resourceCodeAndName[0])
    )
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    // const codes = resourceTypesAndNames.map((x: [string, string]) => x[0])
    // console.log(`codes: ${codes}`)

    return resourceTypesAndNames
  }

  // Resolve promise for data
  let lang0ResourceTypesAndNames: Array<[string, string]>
  $: {
    if (lang0Code) {
      getResourceTypes(lang0Code, [...$otBookStore, ...$ntBookStore])
        .then(resourceTypesAndNames => {
          lang0ResourceTypesAndNames = resourceTypesAndNames
        })
        .catch(err => console.error(err))
    }
  }

  // Resolve promise for data for language
  let lang1ResourceTypesAndNames: Array<[string, string]>
  $: {
    if (lang1Code) {
      getResourceTypes(lang1Code, [...$otBookStore, ...$ntBookStore])
        .then(resourceTypesAndNames => {
          lang1ResourceTypesAndNames = resourceTypesAndNames
        })
        .catch(err => console.error(err))
    }
  }

  // Maintain the checkbox states reactively
  let lang0ResourceTypesCheckboxStates: Array<boolean> = []
  $: {
    if (lang0ResourceTypesAndNames) {
      for (const [idx, resourceTypeAndName] of lang0ResourceTypesAndNames.entries()) {
        if ($lang0ResourceTypesStore && resourceTypeAndName) {
          lang0ResourceTypesCheckboxStates[idx] = $lang0ResourceTypesStore.some(
            item => item[0] === resourceTypeAndName[0]
          )
        } else {
          lang0ResourceTypesCheckboxStates[idx] = false
        }
      }
    }
  }

  // Maintain the checkbox states reactively
  let lang1ResourceTypesCheckboxStates: Array<boolean> = []
  $: {
    if (lang1ResourceTypesAndNames) {
      for (const [idx, resourceTypeAndName] of lang1ResourceTypesAndNames.entries()) {
        if ($lang1ResourceTypesStore && resourceTypeAndName) {
          lang1ResourceTypesCheckboxStates[idx] = $lang1ResourceTypesStore.some(
            item => item[0] === resourceTypeAndName[0]
          )
        } else {
          lang1ResourceTypesCheckboxStates[idx] = false
        }
      }
    }
  }

  function selectAllLang0ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      lang0ResourceTypesStore.set(lang0ResourceTypesAndNames)
    } else {
      lang0ResourceTypesStore.set([])
    }
  }

  function selectAllLang1ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      lang1ResourceTypesStore.set(lang1ResourceTypesAndNames)
    } else {
      lang1ResourceTypesStore.set([])
    }
  }

  const resetResourceTypes = () => {
    lang0ResourceTypesStore.set([])
    lang1ResourceTypesStore.set([])
  }

  function submitResourceTypes() {
    push('#/')
  }

  // Keep track of how many resources are currently stored reactively.
  let nonEmptyLang0Resourcetypes: boolean
  $: nonEmptyLang0Resourcetypes = $lang0ResourceTypesStore.every(item => item.length > 0)

  let nonEmptyLang1Resourcetypes: boolean
  $: nonEmptyLang1Resourcetypes = $lang1ResourceTypesStore.every(item => item.length > 0)

  let resourceTypesCount: number
  $: {
    if (nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCount =
        $lang0ResourceTypesStore.length + $lang1ResourceTypesStore.length
    } else if (nonEmptyLang0Resourcetypes && !nonEmptyLang1Resourcetypes) {
      resourceTypesCount = $lang0ResourceTypesStore.length
    } else if (!nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCount = $lang1ResourceTypesStore.length
    } else {
      resourceTypesCount = 0
    }
  }
</script>

{#if $lang0NameAndCode && $lang1NameAndCode}
  <div>
    {#if !(lang0ResourceTypesAndNames && lang0ResourceTypesCheckboxStates)}
      <LoadingIndicator />
    {:else}
      <h3 class="text-xl capitalize">Resource types header goes here</h3>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <h3>An appropriate header goes here</h3>
          {#if lang0ResourceTypesAndNames.length > 0}
            <div>
              <label for="select-all-lang0-resource-types"
                ><strong>Select all {lang0Name}'s resource types</strong></label
              >
              <input
                id="select-all-lang0-resource-types"
                type="checkbox"
                class="checkbox"
                on:change={event => selectAllLang0ResourceTypes(event)}
              />
            </div>
          {/if}
          <ul>
            {#each lang0ResourceTypesAndNames as resourceTypeAndName, i}
              <li>
                <label for="lang0-resourcetype-{i}">{resourceTypeAndName[1]}</label>
                <input
                  id="lang0-resourcetype-{i}"
                  type="checkbox"
                  bind:group={$lang0ResourceTypesStore}
                  value={resourceTypeAndName}
                  bind:checked={lang0ResourceTypesCheckboxStates[i]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  </div>
  <div>
    {#if !(lang1ResourceTypesAndNames && lang1ResourceTypesCheckboxStates)}
      <LoadingIndicator />
    {:else}
      <h3 class="text-xl capitalize">Resource types header goes here</h3>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <h3>An appropriate header here</h3>
          {#if lang1ResourceTypesAndNames.length > 0}
            <div>
              <label for="select-all-lang1-resource-types"
                >Select all
                {lang1Name}'s resource types</label
              >
              <input
                id="select-all-lang1-resource-types"
                type="checkbox"
                class="checkbox"
                on:change={event => selectAllLang1ResourceTypes(event)}
              />
            </div>
          {/if}
          <ul>
            {#each lang1ResourceTypesAndNames as resourceTypeAndName, i}
              <li>
                <label for="lang1-resourcetype-{i}">{resourceTypeAndName[1]}</label>
                <input
                  id="lang1-resourcetype-{i}"
                  type="checkbox"
                  bind:group={$lang1ResourceTypesStore}
                  value={resourceTypeAndName}
                  bind:checked={lang1ResourceTypesCheckboxStates[i]}
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

{#if resourceTypesCount > 0}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={submitResourceTypes} class="btn"
      >Add ({resourceTypesCount}) Resource Types</button
    >
  </div>

  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetResourceTypes} class="btn"
      >Reset resource types</button
    >
  </div>
{/if}
