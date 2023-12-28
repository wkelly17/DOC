<script lang="ts">
  import WizardBasketModal from './WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import LanguageSearchAndButtons from './LanguageSearchAndButtons.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import {
    langCodesStore,
    langNamesStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import { ntBookStore, otBookStore, bookCountStore } from '../stores/BooksStore'
  import { getApiRootUrl, getCode, getName, getResourceTypeLangCode } from '../lib/utils'
  import {
    resourceTypesStore,
    resourceTypesCountStore
  } from '../stores/ResourceTypesStore'

  let showGatewayLanguages = true
  // If user has previously chosen (during this session, i.e., prior
  // to browser reload) any heart languages and no gateway languages then default to
  // showing the heart languages, otherwise the default stands of
  // showing the gateway languages.
  $: {
    if ($heartCodeAndNamesStore.length > 0 && $gatewayCodeAndNamesStore.length === 0) {
      showGatewayLanguages = false
    }
  }
  // For use by Mobile UI
  let showFilterMenu = false
  let showWizardBasketModal = false

  async function getLangCodesNames(
    apiRootUrl: string = getApiRootUrl(),
    langCodesAndNamesUrl: string = <string>import.meta.env.VITE_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string, boolean]>> {
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
      gatewayCodesAndNames = langCodeNameAndTypes_
        .filter((element: [string, string, boolean]) => {
          return element[2]
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)

      // Filter set of all languages for heart languages
      heartCodesAndNames = langCodeNameAndTypes_
        .filter((element: [string, string, boolean]) => {
          return !element[2]
        })
        .map(tuple => `${tuple[0]}, ${tuple[1]}`)
    })
    .catch(err => console.log(err)) // FIXME Trigger toast for error

  let nonEmptyGatewayLanguages: boolean
  $: nonEmptyGatewayLanguages = $gatewayCodeAndNamesStore.every(item => item.length > 0)

  let nonEmptyHeartLanguages: boolean
  $: nonEmptyHeartLanguages = $heartCodeAndNamesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyGatewayLanguages && nonEmptyHeartLanguages) {
      // Set the langCountStore
      $langCountStore = $gatewayCodeAndNamesStore.length + $heartCodeAndNamesStore.length

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      for (let stringTuple of $heartCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      $langCodesStore = codes

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      for (let stringTuple of $heartCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      $langNamesStore = names

      // Set the resourceTypesStore
      $resourceTypesStore = $resourceTypesStore.filter(
        item =>
          $langCodesStore[0] === getResourceTypeLangCode(item) ||
          $langCodesStore[1] === getResourceTypeLangCode(item)
      )

      // Set the resourceTypesCountStore
      $resourceTypesCountStore = $resourceTypesStore.length
    } else if (nonEmptyGatewayLanguages && !nonEmptyHeartLanguages) {
      // Set the langCountStore
      $langCountStore = $gatewayCodeAndNamesStore.length

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      $langCodesStore = codes

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $gatewayCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      $langNamesStore = names

      // Set the resourceTypesStore
      $resourceTypesStore = $resourceTypesStore.filter(
        item =>
          $langCodesStore[0] === getResourceTypeLangCode(item) ||
          $langCodesStore[1] === getResourceTypeLangCode(item)
      )

      // Set the resourceTypesCountStore
      $resourceTypesCountStore = $resourceTypesStore.length
    } else if (!nonEmptyGatewayLanguages && nonEmptyHeartLanguages) {
      // Set the langCountStore
      $langCountStore = $heartCodeAndNamesStore.length

      // Set the langCodesStore
      let codes = []
      for (let stringTuple of $heartCodeAndNamesStore) {
        codes.push(getCode(stringTuple))
      }
      $langCodesStore = codes

      // Set the langNamesStore
      let names = []
      for (let stringTuple of $heartCodeAndNamesStore) {
        names.push(getName(stringTuple))
      }
      $langNamesStore = names

      // Set the resourceTypesStore
      $resourceTypesStore = $resourceTypesStore.filter(
        item =>
          $langCodesStore[0] === getResourceTypeLangCode(item) ||
          $langCodesStore[1] === getResourceTypeLangCode(item)
      )

      // Set the resourceTypesCountStore
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      $langCountStore = 0
      $langCodesStore = []
      $langNamesStore = []
      $resourceTypesStore = []
      $resourceTypesCountStore = 0
      $otBookStore = []
      $ntBookStore = []
      $bookCountStore = 0
    }
  }

  // Search field handling for gateway languages
  let gatewaySearchTerm: string = ''
  let filteredGatewayCodeAndNames: Array<string> = []
  $: {
    if (gatewayCodesAndNames) {
      filteredGatewayCodeAndNames = gatewayCodesAndNames.filter((item: string) =>
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

  let windowWidth: number
  $: console.log(`windowWidth: ${windowWidth}`)

  const TAILWIND_SM_MIN_WIDTH = 640
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-x-hidden overflow-y-auto">
  <!-- center -->
  <div class="flex-1 flex flex-col sm:w-2/3 bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal leading-[48px]">
      Select up to 2 languages
    </h3>
    <LanguageSearchAndButtons
      {langCodeNameAndTypes}
      {showGatewayLanguages}
      {gatewaySearchTerm}
      {heartSearchTerm}
      {showFilterMenu}
      {showWizardBasketModal}
    />
    {#if gatewayCodesAndNames && gatewayCodesAndNames.length > 0 && heartCodesAndNames && heartCodesAndNames.length > 0}
      {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
        <MobileLanguageDisplay
          {showGatewayLanguages}
          {gatewayCodesAndNames}
          {heartCodesAndNames}
          {filteredHeartCodeAndNames}
          {filteredGatewayCodeAndNames}
        />
      {:else}
        <DesktopLanguageDisplay
          {showGatewayLanguages}
          {gatewayCodesAndNames}
          {heartCodesAndNames}
          {filteredHeartCodeAndNames}
          {filteredGatewayCodeAndNames}
        />
      {/if}
    {/if}
  </div>

  <!-- if isMobile -->
  {#if showWizardBasketModal}
    <WizardBasketModal
      title="Your selections"
      open={showWizardBasketModal}
      on:close={() => (showWizardBasketModal = false)}
    >
      <svelte:fragment slot="body">
        <WizardBasket />
      </svelte:fragment>
    </WizardBasketModal>
  {/if}
  <!-- else -->
  <div class="hidden sm:w-1/3 sm:flex">
    <WizardBasket />
  </div>
  <!-- end if -->
</div>

<style global lang="postcss">
  * :global(.checkbox-dark-bordered) {
    border-color: #1a130b;
    border-radius: 3px;
    width: 1em;
    height: 1em;
  }
  #filter-gl-langs,
  #filter-non-gl-langs {
    text-indent: 17px;
    padding-left: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }
  div.target:has(input[type='checkbox']:checked) {
    background: #e6eefb;
  }
  div.target:has(input[type='radio']:checked) {
    background: #e6eefb;
  }
  input.checkbox-dark-bordered[type='checkbox']:checked + label  {
    color: #015ad9;
  }
</style>
