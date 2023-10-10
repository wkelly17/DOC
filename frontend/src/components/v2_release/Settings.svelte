<script lang="ts">
  import type { SelectElement } from '../../types'
  import Switch from './Switch.svelte'
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import WizardBasketModal from './WizardBasketModal.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    limitTwStore,
    documentRequestKeyStore,
    settingsUpdated
  } from '../../stores/v2_release/SettingsStore'
  import { documentReadyStore } from '../../stores/v2_release/NotificationStore'
  import {
    resourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import { langCodesStore, langCountStore } from '../../stores/v2_release/LanguagesStore'
  import { bookCountStore } from '../../stores/v2_release/BooksStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import LogRocket from 'logrocket'

  let bookLanguageOrderStrategy: SelectElement = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let languageBookOrderStrategy: SelectElement = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let verse: SelectElement = {
    id: 'verse',
    label: <string>import.meta.env.VITE_CHUNK_SIZE_VERSE
  }
  let chapter: SelectElement = {
    id: 'chapter',
    label: <string>import.meta.env.VITE_CHUNK_SIZE_CHAPTER
  }
  // Set default value of chapter
  $assemblyStrategyChunkSizeStore = chapter.id

  // Set up the values for the select drop-downs
  let assemblyStrategies = [bookLanguageOrderStrategy, languageBookOrderStrategy]
  let assemblyStrategyChunkSizes = [chapter, verse]

  const assemblyStrategyHeader = <string>import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER

  const assemblyStrategyChunkingHeader = <string>(
    import.meta.env.VITE_ASSEMBLY_STRATEGY_CHUNKING_HEADER
  )

  $: console.log(`$assemblyStrategyKindStore: ${$assemblyStrategyKindStore}`)
  $: console.log(`$assemblyStrategyChunkSizeStore: ${$assemblyStrategyChunkSizeStore}`)
  $: {
    if ($layoutForPrintStore) {
      $generatePdfStore = true
      $generateDocxStore = false
      $generateEpubStore = false
      $docTypeStore = 'pdf'
    } else {
      $generatePdfStore = true
      $generateDocxStore = false
      $generateEpubStore = false
      $docTypeStore = 'pdf'
    }
  }

  // Set whether TW has been requested for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let regexp = new RegExp('.*tw.*')
  $: {
    if ($resourceTypesStore) {
      console.log('about to check for tw')
      twResourceRequestedStore.set($resourceTypesStore.some(item => regexp.test(item)))
    }
  }
  $: {
       if ($twResourceRequestedStore) {
         limitTwStore.set(true)
       } else {
         limitTwStore.set(false)
       }
  }
  $: console.log(`limitTwStore: ${$limitTwStore}`)

  // The 3rd party HTML to PDF conversion library we use, weasyprint,
  // doesn't seem to be able to handle line length for the Khmer language
  // which results in words overlapping each other when two column
  // layout of Khmer content is displayed. Only TN and TQ resource types
  // use two column layout and thus if those are selected by the user
  // then the UI will exclude PDF as an output format choice.
  let kmRegexp = new RegExp("km, tn, .*|km, tq, .*")
  let showPdfAsOption: boolean = true
  $: console.log(`showPdfAsOption: ${showPdfAsOption}`)
  $: {
    if ($resourceTypesStore) {
      if ($resourceTypesStore.some(item => kmRegexp.test(item))) {
        showPdfAsOption = false
      }
    }
  }

  $: showEmail = false
  $: showEmailCaptured = false
  $: documentReadyStore.set(false)

  // Deal with empty string case
  if ($emailStore && $emailStore === '') {
    emailStore.set(null)
    LogRocket.identify($documentRequestKeyStore)
    // Deal with undefined case
  } else if ($emailStore === undefined) {
    emailStore.set(null)
    LogRocket.identify($documentRequestKeyStore)
    // Deal with non-empty string
  } else if ($emailStore && $emailStore !== '') {
    emailStore.set($emailStore.trim())
    // LogRocket init call happens in App.svelte.
    // Send email to LogRocket using identify.
    LogRocket.identify($emailStore)
  }

  let showWizardBasketModal = false
  $: console.log(`showWizardBasketModal: ${showWizardBasketModal}`)


</script>


<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col sm:w-2/3 bg-white">
    <h3 class="bg-white text-[#33445C] text-4xl mb-8 mt-2 ml-4">Generate document</h3>

     <!-- mobile basket modal launcher -->
    <div class="sm:hidden text-right mr-4">
      <button on:click={() => (showWizardBasketModal = true)}>
        <div class="relative">
          <svg width="56" height="48" viewBox="0 0 56 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z" fill="#33445C"/>
            <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB"/>
          </svg>
          {#if $langCountStore > 0 || $bookCountStore > 0 ||
            $resourceTypesCountStore > 0}
            <!-- badge -->
            <div class="text-center absolute -top-0.5 -right-0.5
                        bg-neutral-focus text-neutral-content
                        rounded-full w-7 h-7" style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);">
              <span class="text-[8px]
                          text-white">{$langCountStore +
                $bookCountStore + $resourceTypesCountStore}</span>
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
            <input name="docType" value={"pdf"}
                   bind:group={$docTypeStore} type="radio"
                   on:change={() => ($settingsUpdated = true)}>
            <span class="text-[#33445C]">{import.meta.env.VITE_PDF_LABEL_V2}</span>
          </label>
        </div>
        {/if}
        <div class="mb-2">
          <label>
            <input name="docType" value={"epub"}
                   bind:group={$docTypeStore} type="radio" on:change={() => ($settingsUpdated = true)}>
            <span class="text-[#33445C]">{import.meta.env.VITE_EPUB_LABEL_V2}</span>
          </label>
        </div>
        <div class="mb-2">
          <label>
            <input name="docType" value={"docx"}
                   bind:group={$docTypeStore} type="radio" on:change={() => ($settingsUpdated = true)}>
            <span class="text-[#33445C]">{import.meta.env.VITE_DOCX_LABEL_V2}</span>
          </label>
        </div>
      </div>

      <h3 class="text-2xl my-2 text-[#33445C]">Layout</h3>
      <div class="ml-4">
        {#if $langCodesStore[1]}
        <div class="flex mb-2">
          <select bind:value="{$assemblyStrategyKindStore}"
                  name="assemblyStrategy" on:change={() => ($settingsUpdated = true)}>
            {#each assemblyStrategies as assemblyStrategy}
            <option value="{assemblyStrategy.id}">
              <span class="text-[#33445C]">{assemblyStrategy.label}</span>
            </option>
            {/each}
          </select>
          <span class="ml-2 text-[#33445C]">{assemblyStrategyHeader}</span>
        </div>
        <div>
          <span class="text-sm text-[#33445C]"
            ><p>
              Choosing 'Mix' will interleave the content for the chosen languages by
              chapter.
            </p>
            <p>
              Choosing 'Separate' will interleave the content for the chosen languages by
              book.
            </p></span
          >
        </div>
        {/if}
        <div class="flex my-2">
          <Switch bind:checked="{$layoutForPrintStore}" id="layout-for-print-store" />
          <span class="text-[#33445C] ml-2">Print Optimization</span>
        </div>
        <div>
          <span class="text-sm text-[#33445C]"
            >Enabling this option will remove extra whitespace</span
          >
        </div>
        {#if $twResourceRequestedStore}
        <div class="flex mt-2">
          <Switch bind:checked="{$limitTwStore}" id="limit-tw-store" />
          <span class="text-[#33445C] ml-2">Limit TW words</span>
        </div>
        <div>
          <span class="text-sm text-[#33445C]"
            >Enabling this option will filter TW words down to only those that occur in
            the books chosen</span
          >
        </div>
        {/if} {#if false}
        <div class="flex justify-between">
          <span class="text-primary-content">{assemblyStrategyChunkingHeader}</span>
          <select
            bind:value="{$assemblyStrategyChunkSizeStore}"
            name="assemblyStrategyChunkSize"
          >
            {#each assemblyStrategyChunkSizes as assemblyStrategyChunkSize}
            <option value="{assemblyStrategyChunkSize.id}">
              <span class="text-primary-content">{assemblyStrategyChunkSize.label}</span>
            </option>
            {/each}
          </select>
        </div>
        <div>
          <span class="text-sm text-neutral-content"
            ><p>
              Choosing 'By Verse' will interleave scripture and helps by a verse's worth
              of content at a time.
            </p>
            <p>
              Choosing 'By Chapter' will interleave scripture and helps by a chapter's
              worth of content at a time.
            </p></span
          >
        </div>
        {/if}
      </div>

      <h3 class="text-2xl my-2 text-[#33445C]">Notification</h3>
      <div class="ml-4">
        {#if !$documentReadyStore}
          <div>
            <input id="emailCheckbox" type="checkbox" on:click={() => (showEmail =
            !showEmail)} value={showEmail} class="checkbox checkbox-dark-bordered" />
            <label for="emailCheckbox" class="text-[#33445C] pl-1"
              >Email me a copy of my document.</label
            >
          </div>
        {/if}
        {#if showEmail && !showEmailCaptured}
          <div>
            <label for="email" class="text-[#33445C] pl-1">Email address</label>
          </div>
          <input
            type="text"
            name="email"
            id="email"
            bind:value="{$emailStore}"
            placeholder="Type email address here (optional)"
            class="input input-bordered bg-white w-full max-w-xs"
            />
          <div>
            <button class="rounded-md bg-[#E6EEFB] text-[#015AD9] px-8
                           py-4 mt-4"
                    on:click={() => (showEmailCaptured = true)}>Submit</button>
          </div>
        {/if}
        {#if showEmailCaptured}
          <div class="text-[#33445C]">
            A copy of your file will be sent to {$emailStore} when it is ready.
          </div>
        {/if}
      </div>

      <GenerateDocument />
    </main>
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
