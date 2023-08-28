<script lang="ts">
  import type { SelectElement } from '../../types'
  import Switch from './Switch.svelte'
  import WizardBreadcrumb from './WizardBreadcrumb.svelte'
  import WizardBasket from './WizardBasket.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    limitTwStore
  } from '../../stores/v2_release/SettingsStore'
  import { documentReadyStore } from '../../stores/v2_release/NotificationStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import { lang1CodeStore } from '../../stores/v2_release/LanguagesStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../../lib/utils'

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
      console.log('Print optimization selected, therefore Docx and ePub output disabled')
    } else {
      $generatePdfStore = true
      $generateDocxStore = false
      $generateEpubStore = false
      $docTypeStore = 'pdf'
      console.log('Print optimization de-selected, set default to pdf')
    }
  }

  // Set whether TW has been requested for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let regexp = new RegExp('.*tw.*')
  $: {
    if ($lang0ResourceTypesStore && $lang1ResourceTypesStore) {
      twResourceRequestedStore.set(
        $lang0ResourceTypesStore.some(item => regexp.test(item)) ||
          $lang1ResourceTypesStore.some(item => regexp.test(item))
      )
    } else if ($lang0ResourceTypesStore && !$lang1ResourceTypesStore) {
      twResourceRequestedStore.set(
        $lang0ResourceTypesStore.some(item => regexp.test(item))
      )
    } else if (!$lang0ResourceTypesStore && $lang1ResourceTypesStore) {
      twResourceRequestedStore.set(
        $lang1ResourceTypesStore.some(item => regexp.test(item))
      )
    }
  }
  $: console.log(`$twResourceRequestedStore: ${$twResourceRequestedStore}`)

  $: showEmail = false
  $: showEmailCaptured = false

  // Deal with empty string case
  if ($emailStore && $emailStore === '') {
    emailStore.set(null)
    // Deal with undefined case
  } else if ($emailStore === undefined) {
    emailStore.set(null)
    // Deal with non-empty string
  } else if ($emailStore && $emailStore !== '') {
    emailStore.set($emailStore.trim())
  }

  // For sidebar
  let open = false

  let showTopMatter: boolean = setShowTopMatter()
</script>

{#if showTopMatter}
<Sidebar bind:open />
<Mast bind:sidebar="{open}" />
<Tabs />
{/if}

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col bg-white">
    <h3 class="bg-white text-[#33445C] text-4xl mb-8 mt-2 ml-4">Generate document</h3>
    <!-- main content -->
    <main class="flex-1 overflow-y-auto p-4">
      <h3 class="text-2xl mt-2 mb-2 text-[#33445C]">File type</h3>
      <div class="ml-4">
        <div class="mb-2">
          <label>
            <input name="docType" value={"pdf"} bind:group={$docTypeStore} type="radio">
            <span class="text-[#33445C]">{import.meta.env.VITE_PDF_LABEL_V2}</span>
          </label>
        </div>
        <!-- {#if $assemblyStrategyKindStore === languageBookOrderStrategy.id && -->
        <!-- !$layoutForPrintStore} -->
        <div class="mb-2">
          <label>
            <input name="docType" value={"epub"} bind:group={$docTypeStore} type="radio">
            <span class="text-[#33445C]">{import.meta.env.VITE_EPUB_LABEL_V2}</span>
          </label>
        </div>
        <div class="mb-2">
          <label>
            <input name="docType" value={"docx"} bind:group={$docTypeStore} type="radio">
            <span class="text-[#33445C]">{import.meta.env.VITE_DOCX_LABEL_V2}</span>
          </label>
        </div>
      </div>

      <h3 class="text-2xl my-2 text-[#33445C]">Layout</h3>
      <div class="ml-4">
        {#if $lang1CodeStore}
        <div class="flex mb-2">
          <select bind:value="{$assemblyStrategyKindStore}" name="assemblyStrategy">
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
        {#if showEmail}
          <div>
            {#if !showEmailCaptured}
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
            {:else}
              <div class="text-[#33445C]">
                A copy of your file will be sent to {$emailStore} when it is ready.
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- {/if} -->
      <GenerateDocument />
    </main>
  </div>

  <WizardBasket />
</div>

<!-- footer -->
<!-- <div class="bg-blue-700 p-4">Footer</div> -->
