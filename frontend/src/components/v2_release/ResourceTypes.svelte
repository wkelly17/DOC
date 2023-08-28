<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import { ntBookStore, otBookStore } from '../../stores/v2_release/BooksStore'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { getApiRootUrl } from '../../lib/utils'

  async function getResourceTypesAndNames(
    langCode: string,
    resourceCodeAndNames: Array<[string, string]>,
    apiRootUrl = getApiRootUrl(),
    sharedResourceTypesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string]>> {
    // NOTE Form the URL to ultimately invoke
    // resource_lookup.shared_resource_types.
    const url_ = `${apiRootUrl}${sharedResourceTypesUrl}${langCode}/`
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

    return resourceTypesAndNames
  }

  let regexp = new RegExp('.*tw.*')
  $: {
    if ($lang0ResourceTypesStore) {
      twResourceRequestedStore.set(
        $lang0ResourceTypesStore.some(item => regexp.test(item))
      )
    }
  }
  $: {
    if ($lang1ResourceTypesStore) {
      twResourceRequestedStore.set(
        $lang1ResourceTypesStore.some(item => regexp.test(item))
      )
    }
  }

  // Resolve promise for data
  let lang0ResourceTypesAndNames: Array<string>
  if ($lang0CodeStore) {
    let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
      item.split(', ')[0],
      item.split(', ')[1]
    ])
    let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
      item.split(', ')[0],
      item.split(', ')[1]
    ])
    getResourceTypesAndNames($lang0CodeStore, [...otResourceCodes_, ...ntResourceCodes_])
      .then(resourceTypesAndNames => {
        lang0ResourceTypesAndNames = resourceTypesAndNames.map(
          tuple => `${tuple[0]}, ${tuple[1]}`
        )

        // If lang0ResourceTypesStore has contents, then assume we are coming
        // back here from the user clicking to edit their resource type
        // selections in the wizard basket, so we want to eliminate
        // any lang0ResourceTypesStore elements that are not in lang0ResourceTypesAndNames.
        if ($lang0ResourceTypesStore.length > 0) {
          lang0ResourceTypesStore.set(
            $lang0ResourceTypesStore.filter(item => {
              return lang0ResourceTypesAndNames.some(element => element === item)
            })
          )
        }
      })
      .catch(err => console.error(err))
  }

  // Resolve promise for data for language
  let lang1ResourceTypesAndNames: Array<string>
  if ($lang1CodeStore) {
    let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
      item.split(', ')[0],
      item.split(', ')[1]
    ])
    let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
      item.split(', ')[0],
      item.split(', ')[1]
    ])
    getResourceTypesAndNames($lang1CodeStore, [...otResourceCodes_, ...ntResourceCodes_])
      .then(resourceTypesAndNames => {
        lang1ResourceTypesAndNames = resourceTypesAndNames.map(
          tuple => `${tuple[0]}, ${tuple[1]}`
        )

        // If lang1ResourceTypesStore has contents, then assume we are coming
        // back here from the user clicking to edit their resource type
        // selections in the wizard basket, so we want to eliminate
        // any lang1ResourceTypesStore elements that are not in lang1ResourceTypesAndNames.
        if ($lang1ResourceTypesStore.length > 0) {
          lang1ResourceTypesStore.set(
            $lang1ResourceTypesStore.filter(item => {
              return lang1ResourceTypesAndNames.some(element => element === item)
            })
          )
        }
      })
      .catch(err => console.error(err))
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

  // Keep track of how many resources are currently stored reactively.
  let nonEmptyLang0Resourcetypes: boolean
  $: nonEmptyLang0Resourcetypes = $lang0ResourceTypesStore.every(item => item.length > 0)

  let nonEmptyLang1Resourcetypes: boolean
  $: nonEmptyLang1Resourcetypes = $lang1ResourceTypesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set(
        $lang0ResourceTypesStore.length + $lang1ResourceTypesStore.length
      )
    } else if (nonEmptyLang0Resourcetypes && !nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang0ResourceTypesStore.length)
    } else if (!nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang1ResourceTypesStore.length)
    } else {
      resourceTypesCountStore.set(0)
    }
  }
</script>

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal leading-[48px]">
      Pick your resources
    </h3>
    <div class="grid grid-cols-2 gap-2 bg-white ml-4 mt-4">
      {#if $langCountStore > 0}
      <div>
        {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length == 0}
        <ProgressIndicator />
        {:else}
        <div>
          <h3 class="text-2xl font-bold text-[#33445C] mb-4">{$lang0NameStore}</h3>
          {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length > 0}
          <div class="flex items-center">
            <input id="select-all-lang0-resource-types" type="checkbox" class="checkbox
            checkbox-dark-bordered" on:change={event =>
            selectAllLang0ResourceTypes(event)} />
            <label for="select-all-lang0-resource-types" class="text-primary-content pl-1"
              >Select all</label
            >
          </div>
          <ul class="pb-4">
            {#each lang0ResourceTypesAndNames as resourceTypeAndName, index}
            <li class="flex items-center">
              <input
                id="lang0-resourcetype-{index}"
                type="checkbox"
                bind:group="{$lang0ResourceTypesStore}"
                value="{resourceTypeAndName}"
                class="checkbox checkbox-dark-bordered"
              />
              <label for="lang0-resourcetype-{index}" class="text-primary-content pl-1"
                >{resourceTypeAndName.split(', ')[1]}</label
              >
            </li>
            {/each}
          </ul>
          {/if}
        </div>
        {/if}
      </div>
      {/if} {#if $langCountStore > 1} {#if !lang1ResourceTypesAndNames}
      <ProgressIndicator />
      {:else}
      <div>
        <h3 class="text-2xl font-bold text-[#33445C] mb-4">{$lang1NameStore}</h3>
        {#if lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length > 0}
        <div class="flex items-center">
          <input id="select-all-lang1-resource-types" type="checkbox" class="checkbox
          checkbox-dark-bordered" on:change={event => selectAllLang1ResourceTypes(event)}
          />
          <label for="select-all-lang1-resource-types" class="text-primary-content pl-1"
            >Select all</label
          >
        </div>
        <ul>
          {#each lang1ResourceTypesAndNames as resourceTypeAndName, index}
          <li class="flex items-center">
            <input
              id="lang1-resourcetype-{index}"
              type="checkbox"
              bind:group="{$lang1ResourceTypesStore}"
              value="{resourceTypeAndName}"
              class="checkbox checkbox-dark-bordered"
            />
            <label for="lang1-resourcetype-{index}" class="text-primary-content pl-1"
              >{resourceTypeAndName.split(', ')[1]}</label
            >
          </li>
          {/each}
        </ul>
        {/if}
      </div>
      {/if} {/if}
    </div>
  </div>

  <WizardBasket />
</div>

<style global lang="postcss">
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
