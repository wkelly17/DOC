<script lang="ts">
  import type { SelectElement } from '../types'
  import Switch from './Switch.svelte'
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import WizardBasketModal from './WizardBasketModal.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    emailStore,
    limitTwStore,
    documentRequestKeyStore,
    settingsUpdated
  } from '../stores/SettingsStore'
  import { documentReadyStore } from '../stores/NotificationStore'
  import {
    resourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore
  } from '../stores/ResourceTypesStore'
  import { langCodesStore, langCountStore } from '../stores/LanguagesStore'
  import { bookCountStore } from '../stores/BooksStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import LogRocket from 'logrocket'

  let chapter: SelectElement = {
    id: 'chapter',
    label: <string>import.meta.env.VITE_CHUNK_SIZE_CHAPTER
  }
  // Set default value of chapter
  $assemblyStrategyChunkSizeStore = chapter.id

  // Set whether TW has been requested for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let regexp = new RegExp('.*tw.*')
  $: {
    if ($resourceTypesStore) {
      $twResourceRequestedStore = $resourceTypesStore.some(item => regexp.test(item))
    }
  }
  $: {
    if ($twResourceRequestedStore) {
      $limitTwStore = true
    } else {
      $limitTwStore = false
    }
  }

  // The 3rd party HTML to PDF conversion library we use, weasyprint,
  // doesn't seem to be able to handle line length for the Khmer language
  // which results in words overlapping each other when two column
  // layout of Khmer content is displayed. Only TN and TQ resource types
  // use two column layout and thus if those are selected by the user
  // then the UI will exclude PDF as an output format choice for
  // Khmer.
  let kmRegexp = new RegExp('km, tn, .*|km, tq, .*')
  let showPdfAsOption: boolean = true
  $: {
    if ($resourceTypesStore) {
      if ($resourceTypesStore.some(item => kmRegexp.test(item))) {
        showPdfAsOption = false
      }
    }
  }

  $: showEmail = false
  $: showEmailCaptured = false
  $: $documentReadyStore = false

  if ($emailStore && $emailStore === '') {
    $emailStore = null
    LogRocket.identify($documentRequestKeyStore)
  } else if ($emailStore === undefined) {
    $emailStore = null
    LogRocket.identify($documentRequestKeyStore)
  } else if ($emailStore && $emailStore !== '') {
    $emailStore = $emailStore.trim()
    // LogRocket init call happens in App.svelte.
    // Tell LogRocket to identify the session via the email provided.
    LogRocket.identify($emailStore)
  }

  let showWizardBasketModal = false
</script>

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col sm:w-2/3 bg-white mx-4 mb-6">
    <h3 class="bg-white text-[#33445C] text-4xl font-normal leading-[48px] mb-4">
      Generate document
    </h3>

    <!-- mobile basket modal launcher -->
    <div class="sm:hidden text-right mr-4">
      <button on:click={() => (showWizardBasketModal = true)}>
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
            <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
          </svg>
          {#if $langCountStore > 0 || $bookCountStore > 0 || $resourceTypesCountStore > 0}
            <!-- badge -->
            <div
              class="text-center absolute -top-0.5 -right-0.5
                        bg-neutral-focus text-[#33445C]
                        rounded-full w-7 h-7"
              style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
            >
              <span class="text-[8px] text-white"
                >{$langCountStore + $bookCountStore + $resourceTypesCountStore}</span
              >
            </div>
          {/if}
        </div>
      </button>
    </div>
    <!-- main content -->
    <main class="flex-1 overflow-y-auto p-4">
      <h3 class="text-2xl mt-2 mb-2 text-[#33445C]">File type</h3>
      <div class="ml-4">
        {#if showPdfAsOption}
          <div class="mb-2">
            <label>
              <input
                name="docType"
                value={'pdf'}
                bind:group={$docTypeStore}
                type="radio"
                on:change={() => ($settingsUpdated = true)}
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span class="text-[#33445C] text-xl">{import.meta.env.VITE_PDF_LABEL}</span>
            </label>
          </div>
        {/if}
        <div class="mb-2">
          <label>
            <input
              name="docType"
              value={'epub'}
              bind:group={$docTypeStore}
              type="radio"
              on:change={() => ($settingsUpdated = true)}
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <span class="text-[#33445C] text-xl">{import.meta.env.VITE_EPUB_LABEL}</span>
          </label>
        </div>
        <div class="mb-2">
          <label>
            <input
              name="docType"
              value={'docx'}
              bind:group={$docTypeStore}
              type="radio"
              on:change={() => ($settingsUpdated = true)}
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <span class="text-[#33445C] text-xl">{import.meta.env.VITE_DOCX_LABEL}</span>
          </label>
        </div>
      </div>
      <h3 class="text-2xl mt-4 mb-2 text-[#33445C]">Layout</h3>
      <div class="ml-4">
        {#if $langCodesStore[1]}
          <div class="mb-2">
            <label>
              <input
                name="assemblyType"
                value={'lbo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => ($settingsUpdated = true)}
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span class="text-[#33445C] text-xl">Interleave content by book</span>
            </label>
          </div>
          <div class="mb-6">
            <label>
              <input
                name="assemblyType"
                value={'blo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => ($settingsUpdated = true)}
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span class="text-[#33445C] text-xl">Interleave content by chapter</span>
            </label>
          </div>
        {/if}
        <div class="flex">
          <Switch bind:checked={$layoutForPrintStore} id="layout-for-print-store" />
          <span class="text-[#33445C] text-xl ml-2">Print optimization</span>
        </div>
        <div class="mt-2">
          <span class="text-lg text-[#33445C]"
            >Enabling this option will remove extra whitespace</span
          >
        </div>
        {#if $twResourceRequestedStore}
          <div class="flex mt-6 mb-2">
            <Switch bind:checked={$limitTwStore} id="limit-tw-store" />
            <span class="text-[#33445C] text-xl ml-2">Limit TW words</span>
          </div>
          <div>
            <span class="text-lg text-[#33445C]"
              >Enabling this option will filter TW words down to only those that occur in
              the books chosen</span
            >
          </div>
        {/if}
      </div>

      <h3 class="text-2xl mt-4 mb-2 text-[#33445C]">Notification</h3>
      <div class="ml-4">
        {#if !$documentReadyStore}
          <div>
            <input
              id="emailCheckbox"
              type="checkbox"
              on:click={() => (showEmail = !showEmail)}
              value={showEmail}
              class="checkbox checkbox-dark-bordered"
            />
            <label for="emailCheckbox" class="text-[#33445C] text-xl pl-1"
              >Email me a copy of my document.</label
            >
          </div>
        {/if}
        {#if showEmail && !showEmailCaptured}
          <div>
            <label for="email" class="text-[#33445C] text-xl pl-1">Email address</label>
          </div>
          <input
            type="text"
            name="email"
            id="email"
            bind:value={$emailStore}
            placeholder="Type email address here (optional)"
            class="input input-bordered bg-white w-full max-w-xs"
          />
          <div>
            <button
              class="rounded-md bg-[#E6EEFB] text-[#015AD9] text-xl px-8
                           py-4 mt-4"
              on:click={() => (showEmailCaptured = true)}>Submit</button
            >
          </div>
        {/if}
        {#if showEmailCaptured}
          <div class="text-[#33445C] text-xl">
            A copy of your file will be sent to {$emailStore} when it is ready.
          </div>
        {/if}
      </div>

      <GenerateDocument />
    </main>
  </div>

  <!-- {#if isMobile} -->
  {#if showWizardBasketModal}
    <WizardBasketModal title="Your selections" bind:showWizardBasketModal>
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
