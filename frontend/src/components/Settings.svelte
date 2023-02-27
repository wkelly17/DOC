<script lang="ts">
  import type { SelectElement } from '../types'
  import Switch from './Switch.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore
  } from '../stores/SettingsStore'
  import { lang1CodeStore } from '../stores/LanguagesStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'

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
      $generateDocxStore = false
      $generateEpubStore = false
      console.log('Print optimization selected, therefore Docx and ePub output disabled')
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

<h3 class="bg-white text-secondary-content text-lg pb-8 pt-2 pl-2">
  Interleave Settings
</h3>
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
  {#if $lang1CodeStore && !$layoutForPrintStore}
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
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <label for="email" class="text-primary-content"
        >{import.meta.env.VITE_EMAIL_LABEL}</label
      >
      <input
        type="text"
        name="email"
        id="email"
        bind:value="{$emailStore}"
        placeholder="Type email address here (optional)"
        class="input input-bordered bg-white w-full max-w-xs"
      />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Providing an email is optional and not required. If you provide an email address
        the system will send the download links for your generated document to your email
        address in addition to showing them on this page.</span
      >
    </div>
  </li>
</ul>
<GenerateDocument />
