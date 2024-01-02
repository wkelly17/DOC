<script lang="ts">
  import WizardBasketModal from './WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import Modal from './Modal.svelte'
  import ProgressIndicator from './ProgressIndicator.svelte'
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

  const TAILWIND_SM_MIN_WIDTH = <number>import.meta.env.VITE_TAILWIND_SM_MIN_WIDTH
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
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !langCodeNameAndTypes || langCodeNameAndTypes.length === 0}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showGatewayLanguages}
            <label id="label-for-filter-gl-langs" for="filter-gl-langs">
              <input
                id="filter-gl-langs"
                bind:value={gatewaySearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white sm:w-full max-w-xs"
              />
            </label>
            <div class="ml-2 hidden sm:flex" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-[#015ad9] text-white font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = true)}
              >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-white text-[#33445C] font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = false)}
              >
                Heart
              </button>
            </div>
            <div class="flex sm:hidden ml-2">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <rect width="56" height="48" rx="12" fill="#001533" />
                    <path
                      d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                      fill="white"
                    />
                  </svg>
                {:else}
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                      fill="#33445C"
                    />
                    <rect
                      x="0.5"
                      y="0.5"
                      width="55"
                      height="47"
                      rx="11.5"
                      stroke="#E5E8EB"
                    />
                  </svg>
                {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
                      fill="#33445C"
                    />
                    <rect
                      x="0.5"
                      y="0.5"
                      width="55"
                      height="47"
                      rx="11.5"
                      stroke="#E5E8EB"
                    />
                  </svg>
                  {#if $langCountStore > 0}
                    <!-- badge -->
                    <div
                      class="text-center absolute -top-0.5 -right-0.5
                                bg-neutral-focus text-neutral-content
                                rounded-full w-7 h-7"
                      style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                    >
                      <span class="text-[8px] text-white">{$langCountStore}</span>
                    </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal title="Filter" bind:showFilterMenu>
                <svelte:fragment slot="body">
                  <label for="show-gateway-radio-button">
                    <div
                      class="flex items-center radio-target
                                h-[48px] pl-4 pr-8 py-2"
                    >
                      <input
                        id="show-gateway-radio-button"
                        type="radio"
                        value={true}
                        bind:group={showGatewayLanguages}
                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <span class="text-[#33445C] pl-1">Gateway languages</span>
                    </div>
                  </label>
                  <label for="show-heart-radio-button">
                    <div
                      class="flex items-center radio-target
                                h-[48px] pl-4 pr-8 py-2"
                    >
                      <input
                        id="show-heart-radio-button"
                        type="radio"
                        value={false}
                        bind:group={showGatewayLanguages}
                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <span class="text-[#33445C] pl-1">Heart languages</span>
                    </div>
                  </label>
                </svelte:fragment>
              </Modal>
            {/if}
          {:else}
            <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
              <input
                id="filter-non-gl-langs"
                bind:value={heartSearchTerm}
                placeholder="Search Languages"
                class="input input-bordered bg-white sm:w-full max-w-xs"
              />
            </label>
            <div class="ml-2 hidden sm:flex" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-white text-[#33445c] font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = true)}
              >
                Gateway
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-[#015ad9]
                        text-white font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showGatewayLanguages = false)}
              >
                Heart
              </button>
            </div>
            <div class="flex sm:hidden ml-2">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <rect width="56" height="48" rx="12" fill="#001533" />
                    <path
                      d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                      fill="white"
                    />
                  </svg>
                {:else}
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                      fill="#33445C"
                    />
                    <rect
                      x="0.5"
                      y="0.5"
                      width="55"
                      height="47"
                      rx="11.5"
                      stroke="#E5E8EB"
                    />
                  </svg>
                {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <svg
                    width="56"
                    height="48"
                    viewBox="0 0 56 48"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
                      fill="#33445C"
                    />
                    <rect
                      x="0.5"
                      y="0.5"
                      width="55"
                      height="47"
                      rx="11.5"
                      stroke="#E5E8EB"
                    />
                  </svg>
                  {#if $langCountStore > 0}
                    <!-- badge -->
                    <div
                      class="text-center absolute -top-0.5 -right-0.5
                              bg-neutral-focus text-neutral-content
                              rounded-full w-7 h-7"
                      style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                    >
                      <span class="text-[8px] text-white">{$langCountStore}</span>
                    </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal title="Filter" bind:showFilterMenu>
                <svelte:fragment slot="body">
                  <label for="show-gateway-radio-button">
                    <div
                      class="flex items-center radio-target
                                h-[48px] pl-4 pr-8 py-2"
                    >
                      <input
                        id="show-gateway-radio-button"
                        type="radio"
                        value={true}
                        bind:group={showGatewayLanguages}
                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <span class="text-[#33445C] pl-1">Gateway languages</span>
                    </div>
                  </label>
                  <label for="show-heart-radio-button">
                    <div
                      class="flex items-center radio-target
                                h-[48px] px-4 py-2"
                    >
                      <input
                        id="show-heart-radio-button"
                        type="radio"
                        value={false}
                        bind:group={showGatewayLanguages}
                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <span class="text-[#33445C] pl-1">Heart languages</span>
                    </div>
                  </label>
                </svelte:fragment>
              </Modal>
            {/if}
          {/if}
        </div>
      {/if}
    </div>
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
  div.radio-target:has(input[type='radio']:checked) {
    background: #e6eefb;
  }
  input.show-gateway-radio-button[type='radio']:checked + span {
    color: #015ad9;
  }
  input.show-heart-radio-button[type='radio']:checked + span {
    color: #015ad9;
  }
  input.checkbox-dark-bordered[type='checkbox']:checked + span {
    color: #015ad9;
  }
  div.target3:has(input[type='checkbox']:checked) + span {
    color: #015ad9;
  }
  div.target2:has(input[type='checkbox']:checked) + div {
    color: #015ad9;
  }
  div.target2:has(input[type='checkbox']:checked) + span {
    color: #015ad9;
  }
</style>
