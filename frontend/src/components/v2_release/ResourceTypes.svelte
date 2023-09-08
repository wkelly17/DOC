<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import { ntBookStore, otBookStore } from '../../stores/v2_release/BooksStore'
  import {
    langCodesStore,
    langNamesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { getApiRootUrl, getCode } from '../../lib/utils'

  async function getResourceTypesAndNames(
    langCode: string,
    resourceCodeAndNames: Array<[string, string]>,
    apiRootUrl = getApiRootUrl(),
    sharedResourceTypesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string, string]>> {
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

    // Associate the langCode to each resource type code and name pair
    return resourceTypesAndNames.map(element => [langCode, element[0], element[1]])
  }

  let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
    item.split(', ')[0],
    item.split(', ')[1]
  ])
  let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
    item.split(', ')[0],
    item.split(', ')[1]
  ])
  // Resolve promise for data
  let lang0ResourceTypesAndNames: Array<string>
  if ($langCodesStore[0]) {
    getResourceTypesAndNames($langCodesStore[0], [
      ...otResourceCodes_,
      ...ntResourceCodes_
    ])
      .then(resourceTypesAndNames => {
        lang0ResourceTypesAndNames = resourceTypesAndNames.map(
          tuple => `${tuple[0]}, ${tuple[1]}, ${tuple[2]}`
        )
      })
      .catch(err => console.error(err))
  }

  // Resolve promise for data for language
  let lang1ResourceTypesAndNames: Array<string>
  if ($langCodesStore[1]) {
    getResourceTypesAndNames($langCodesStore[1], [
      ...otResourceCodes_,
      ...ntResourceCodes_
    ])
      .then(resourceTypesAndNames => {
        lang1ResourceTypesAndNames = resourceTypesAndNames.map(
          tuple => `${tuple[0]}, ${tuple[1]}, ${tuple[2]}`
        )
      })
      .catch(err => console.error(err))
  }

  let nonEmptyResourcetypes: boolean
  $: nonEmptyResourcetypes = $resourceTypesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyResourcetypes) {
      resourceTypesCountStore.set($resourceTypesStore.length)
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
          <h3 class="text-2xl font-bold text-[#33445C] mb-4">{$langNamesStore[0]}</h3>
          {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length > 0}
          <ul class="pb-4">
            {#each lang0ResourceTypesAndNames as lang0ResourceTypeAndName, index}
            <li class="flex items-center">
              <input
                id="lang0-resourcetype-{index}"
                type="checkbox"
                bind:group="{$resourceTypesStore}"
                value="{lang0ResourceTypeAndName}"
                class="checkbox checkbox-dark-bordered"
              />
              <label for="lang0-resourcetype-{index}" class="text-primary-content pl-1"
                >{lang0ResourceTypeAndName.split(', ')[2]}</label
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
        <h3 class="text-2xl font-bold text-[#33445C] mb-4">{$langNamesStore[1]}</h3>
        {#if lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length > 0}
        <ul>
          {#each lang1ResourceTypesAndNames as lang1ResourceTypeAndName, index}
          <li class="flex items-center">
            <input
              id="lang1-resourcetype-{index}"
              type="checkbox"
              bind:group="{$resourceTypesStore}"
              value="{lang1ResourceTypeAndName}"
              class="checkbox checkbox-dark-bordered"
            />
            <label for="lang1-resourcetype-{index}" class="text-primary-content pl-1"
              >{lang1ResourceTypeAndName.split(', ')[2]}</label
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
