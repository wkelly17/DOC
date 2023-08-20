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
  import { twResourceRequestedStore } from '../../stores/v2_release/ResourceTypesStore'
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

<h3 class="bg-white text-secondary-content text-lg pb-8 pt-2 pl-2">Document Settings</h3>
<ul>
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="text-primary-content">Print Optimization</span>
      <Switch bind:checked="{$layoutForPrintStore}" id="layout-for-print-store" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will remove extra whitespace</span
      >
    </div>
  </li>
  {#if $twResourceRequestedStore}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="text-primary-content">Limit TW words</span>
      <Switch bind:checked="{$limitTwStore}" id="limit-tw-store" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will filter TW words down to only those that occur in the
        books chosen</span
      >
    </div>
  </li>
  {/if} {#if !$documentReadyStore && $lang1CodeStore && !$layoutForPrintStore}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="text-primary-content">{assemblyStrategyHeader}</span>
      <select bind:value="{$assemblyStrategyKindStore}" name="assemblyStrategy">
        {#each assemblyStrategies as assemblyStrategy}
        <option value="{assemblyStrategy.id}">
          <span class="text-primary-content">{assemblyStrategy.label}</span>
        </option>
        {/each}
      </select>
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        ><p>Choosing 'Mix' will interleave the content of two languages for each book.</p>
        <p>
          Choosing 'Separate' will keep the content of each book separated by language.
        </p></span
      >
    </div>
  </li>
  {/if} {#if false}
  <li class="bg-white p-2">
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
          Choosing 'By Verse' will interleave scripture and helps by a verse's worth of
          content at a time.
        </p>
        <p>
          Choosing 'By Chapter' will interleave scripture and helps by a chapter's worth
          of content at a time.
        </p></span
      >
    </div>
  </li>
  {/if}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <label>
        <input name="docType" value={"pdf"} bind:group={$docTypeStore} type="radio">
        <span class="text-primary-content">{import.meta.env.VITE_PDF_LABEL}</span>
      </label>
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will generate a PDF of the document.</span
      >
    </div>
  </li>
  {#if $assemblyStrategyKindStore === languageBookOrderStrategy.id &&
  !$layoutForPrintStore}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <label>
        <input name="docType" value={"epub"} bind:group={$docTypeStore} type="radio">
        <span class="text-primary-content">{import.meta.env.VITE_EPUB_LABEL}</span>
      </label>
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will generate an ePub of the document.</span
      >
    </div>
  </li>
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <label>
        <input name="docType" value={"docx"} bind:group={$docTypeStore} type="radio">
        <span class="text-primary-content">{import.meta.env.VITE_DOCX_LABEL}</span>
      </label>
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will generate a Docx of the document.</span
      >
    </div>
  </li>
  {/if}
</ul>
<GenerateDocument />
<WizardBasket />
