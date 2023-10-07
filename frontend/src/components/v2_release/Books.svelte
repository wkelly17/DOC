<script lang="ts">
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import otBooks from '../../data/ot_books'
  import { ntBookStore, otBookStore, bookCountStore } from '../../stores/v2_release/BooksStore'
  import {
    langCodesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { getApiRootUrl, getCode, getName } from '../../lib/utils'
  import Modal from './Modal.svelte'
  import WizardBasketModal from './WizardBasketModal.svelte'

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
  let otResourceCodes: Array<string>
  let ntResourceCodes: Array<string>
  if ($langCountStore > 1) {
    getSharedResourceCodesAndNames($langCodesStore[0], $langCodesStore[1])
      .then(resourceCodesAndNames => {
        // Filter set of all resource codes into old testament
        // resource codes.
        otResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If otBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any otBookStore elements that are not in otResourceCodes.
        if ($otBookStore.length > 0) {
          otBookStore.set($otBookStore.filter(item => {
            return otResourceCodes.some(element => element === item)
          }))
        }

        // Filter set of all resource codes into new testament
        // resource codes.
        ntResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return !otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)


        // If ntBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any ntBookStore elements that are not in ntResourceCodes.
        if ($ntBookStore.length > 0) {
          ntBookStore.set($ntBookStore.filter(item => {
            return ntResourceCodes.some(element => element === item)
          }))
        }
      })
      .catch(err => console.error(err))
  } else {
    getResourceCodesAndNames($langCodesStore[0])
      .then(resourceCodesAndNames => {
        // Filter set of all resource codes into old testament
        // resource codes.
        otResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If otBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any otBookStore elements that are not in otResourceCodes.
        if ($otBookStore.length > 0) {
          otBookStore.set($otBookStore.filter(item => {
            return otResourceCodes.some(element => element === item)
          }))
        }

        // Filter set of all resource codes into new testament
        // resource codes.
        ntResourceCodes = resourceCodesAndNames
          .filter((element: [string, string]) => {
            return !otBooks.some(item => item === element[0])
          })
          .map(tuple => `${tuple[0]}, ${tuple[1]}`)

        // If ntBookStore has contents, then assume we are coming
        // back here from the user clicking to edit their book
        // selections in the wizard basket, so we want to eliminate
        // any ntBookStore elements that are not in ntResourceCodes.
        if ($ntBookStore.length > 0) {
          ntBookStore.set($ntBookStore.filter(item => {
            return ntResourceCodes.some(element => element === item)
          }))
        }
      })
      .catch(err => console.error(err))
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
  let showOldTestament = false
  let showFilterMenu = false
  $: console.log(`showFilterMenu: ${showFilterMenu}`)
  let showWizardBasketModal = false
  $: console.log(`showWizardBasketModal: ${showWizardBasketModal}`)

</script>


<WizardBreadcrumb />


<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-x-hidden overflow-y-auto">
  <!-- center -->
  <div class="flex-1 flex flex-col sm:w-2/3 bg-white">
    <h3 class="ml-4 text-[#33445C] text-4xl font-normal
               leading-[48px]">Select books</h3>

    <!-- search and buttons -->
    <div class="flex items-center px-2 py-2 mt-2 bg-white">
      {#if !otResourceCodes || !ntResourceCodes}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showOldTestament}
            <label>
            <input
              id="filter-ot-books"
              bind:value={otSearchTerm}
              placeholder="Search OT books"
              class="input input-bordered bg-white w-full max-w-xs"
              />
            </label>
            <div class="hidden sm:flex ml-2" role="group">
              <button class="rounded-l-md w-36 h-10 bg-[#015ad9]
                             text-white font-medium
                             leading-tight border-x-2 border-t-2
                             border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
                      on:click={() => (showOldTestament = true)}>
                Old Testament
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-white text-[#33445c] font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
                >
                New Testament
              </button>
            </div>
            <div class="flex sm:hidden ml-2">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="56" height="48" rx="12" fill="#001533"/>
                    <path d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z" fill="white"/>
                  </svg>
                {:else}
                  <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z" fill="#33445C"/>
                    <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB"/>
                  </svg>
                {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z" fill="#33445C"/>
                    <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB"/>
                  </svg>
                  {#if $langCountStore > 0 || $bookCountStore > 0}
                    <!-- badge -->
                    <div class="text-center absolute -top-0.5 -right-0.5
                                bg-neutral-focus text-neutral-content
                                rounded-full w-7 h-7" style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);">
                      <span class="text-[8px]
                                   text-white">{$langCountStore + $bookCountStore}</span>
                    </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal
                title="Filter"
                open={showFilterMenu}
                on:close={() => (showFilterMenu = false)}
                >
                <svelte:fragment slot="body">
                  <div class="flex items-center">
                    <input
                      id="show-ot-radio-button"
                      type="radio"
                      value={true}
                      bind:group={showOldTestament}
                      class="radio checked:bg-[#015ad9]"
                      />
                    <label for="show-ot-radio-button"
                           class="text-[#33445C] pl-1">Old Testament</label>
                  </div>
                  <div class="flex items-center">
                    <input
                      id="show-nt-radio-button"
                      type="radio"
                      value={false}
                      bind:group={showOldTestament}
                      class="radio checked:bg-[#015ad9]"
                      />
                    <label for="show-nt-radio-button"
                           class="text-[#33445C] pl-1">New Testament</label>
                  </div>
                </svelte:fragment>
              </Modal>
            {/if}
          {:else}
            <label>
              <input
                id="filter-nt-books"
                bind:value={ntSearchTerm}
                placeholder="Search NT books"
                class="input input-bordered bg-white sm:w-full max-w-xs"
                />
            </label>
            <div class="hidden sm:flex ml-2" role="group">
              <button
                class="rounded-l-md w-36 h-10 bg-white text-[#33445c]
                       font-medium leading-tight border-x-2
                       border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = true)}
                >
                Old Testament
              </button>
              <button
                class="rounded-r-md w-36 h-10 bg-[#015ad9]
                       text-white font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
                on:click={() => (showOldTestament = false)}
                >
                New Testament
              </button>
            </div>
            <div class="flex sm:hidden ml-2">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="56" height="48" rx="12" fill="#001533"/>
                    <path d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z" fill="white"/>
                  </svg>

                  {:else}
                    <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z" fill="#33445C"/>
                      <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB"/>
                    </svg>
                  {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z" fill="#33445C"/>
                    <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB"/>
                  </svg>
                  {#if $langCountStore > 0 || $bookCountStore > 0}
                    <!-- badge -->
                  <div class="text-center absolute -top-0.5 -right-0.5
                              bg-neutral-focus text-neutral-content
                              rounded-full w-7 h-7" style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);">
                    <span class="text-[8px]
                                 text-white">{$langCountStore + $bookCountStore}</span>
                  </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal
                title="Filter"
                open={showFilterMenu}
                on:close={() => (showFilterMenu = false)}
                >
                <svelte:fragment slot="body">
                  <div class="flex items-center">
                    <input
                      id="show-gateway-radio-button"
                      type="radio"
                      value={true}
                      bind:group={showOldTestament}
                      class="radio checked:bg-[#015ad9]"
                      />
                    <label for="show-gateway-radio-button"
                           class="text-[#33445C] pl-1">Old Testament</label>
                  </div>
                  <div class="flex items-center">
                    <input
                      id="show-heart-radio-button"
                      type="radio"
                      value={false}
                      bind:group={showOldTestament}
                      class="radio checked:bg-[#015ad9]"
                      />
                    <label for="show-heart-radio-button"
                           class="text-[#33445C] pl-1">New Testament</label>
                  </div>
                </svelte:fragment>
              </Modal>
            {/if}
          {/if}
        </div>
      {/if}
    </div>

    {#if $langCountStore > 0}

      <!-- main content -->
      <main class="flex-1 overflow-y-auto p-4">
        {#if showOldTestament}
          {#if otResourceCodes?.length > 0}
            <div class="flex items-center">
              <input
                id="select-all-old-testament"
                type="checkbox"
                class="checkbox checkbox-dark-bordered"
                on:change={event => selectAllOtResourceCodes(event)}
              />
              <label for="select-all-old-testament"
                    class="text-secondary-content pl-1"
                    >Select all</label>
            </div>
          {/if}
          {#if otResourceCodes?.length > 0}
            {#each otResourceCodes as resourceCodeAndName, index}
              <div style={filteredOtResourceCodes.includes(resourceCodeAndName) ? '' : 'display: none'}
                   class="flex items-center"
                   >
                <input
                  id="lang-resourcecode-ot-{index}"
                  type="checkbox"
                  bind:group={$otBookStore}
                  value={resourceCodeAndName}
                  class="checkbox checkbox-dark-bordered"
                  />
                <label for="lang-resourcecode-ot-{index}"
                       class="text-secondary-content pl-1"
                       >{getName(resourceCodeAndName)}</label>
              </div>
            {/each}
          {/if}
        {:else}
          {#if ntResourceCodes?.length > 0}
            <div class="flex items-center">
              <input
                id="select-all-new-testament"
                type="checkbox"
                class="checkbox checkbox-dark-bordered"
                on:change={event => selectAllNtResourceCodes(event)}
              />
              <label for="select-all-new-testament"
                    class="text-secondary-content pl-1"
                    >Select all</label>
            </div>
          {/if}
          {#if ntResourceCodes?.length > 0}
            {#each ntResourceCodes as resourceCodeAndName, index}
              <div style={filteredNtResourceCodes.includes(resourceCodeAndName) ? '' : 'display: none'}
                   class="flex items-center"
                   >
                <input
                  id="lang-resourcecode-nt-{index}"
                  type="checkbox"
                  bind:group={$ntBookStore}
                  value={resourceCodeAndName}
                  class="checkbox checkbox-dark-bordered"
                  />
                <label for="lang-resourcecode-nt-{index}"
                       class="text-secondary-content pl-1"
                       >{getName(resourceCodeAndName)}</label>
              </div>
            {/each}
          {/if}
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
      </main>
    {/if}
  </div>

  <!-- {#if isMobile} -->
  {#if showWizardBasketModal}
    <WizardBasketModal
      title="Your selections"
      open={showWizardBasketModal}
      on:close={() => (showWizardBasketModal = false)}>
      <svelte:fragment slot="body">
        <WizardBasket />
      </svelte:fragment>
    </WizardBasketModal>
  {/if}
  <!-- {:else} -->
  <div class="hidden sm:w-1/3 sm:flex">
    <WizardBasket />
  </div>
  <!-- {/if} -->

</div>


<style global lang="postcss">
  #filter-ot-books, #filter-nt-books {
    text-indent: 17px;
    padding-left: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }

  * :global(.checkbox-dark-bordered) {
    border-color: #1a130b;
    border-radius: 3px;
    width: 1em;
    height: 1em;
  }

  input[type="checkbox"]:checked + label {
    background: #e6eefb;
  }
  input[type="radio"]:checked + label {
    background: #e6eefb;
  }
</style>
