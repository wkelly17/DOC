<script lang="ts">
  import type { AssemblyStrategy } from '../types'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore
  } from '../stores/SettingsStore'
  import { lang1CodeStore } from '../stores/LanguagesStore'
  import GenerateDocument from './GenerateDocument.svelte'

  let book_language_order_strategy: AssemblyStrategy = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let language_book_order_strategy: AssemblyStrategy = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let assemblyStrategies = [book_language_order_strategy, language_book_order_strategy]

  const assemblyStrategyHeader = <string>import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER

  $: console.log(`$assemblyStrategyKindStore: ${$assemblyStrategyKindStore}`)
</script>

<h3 class="bg-primary text-secondary-content text-lg pb-8 pt-2 pl-2">
  Interleave Settings
</h3>
<ul>
  <li class="bg-primary p-2">
    <div class="flex justify-between">
      <span class="text-neutral-content">Print Optimization</span>
      <input type="checkbox" bind:checked={$layoutForPrintStore} class="toggle" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will remove extra whitespace</span
      >
    </div>
  </li>
  {#if $lang1CodeStore}
    <li class="bg-primary p-2">
      <div class="flex justify-between">
        <span class="text-neutral-content">{assemblyStrategyHeader}</span>
        <select bind:value={$assemblyStrategyKindStore} name="assemblyStrategy">
          {#each assemblyStrategies as assemblyStrategy}
            <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option>
          {/each}
        </select>
      </div>
      <div>
        <span class="text-sm text-neutral-content"
          ><p>
            Choosing 'Mix' will interleave the content of two languages verse by verse.
          </p>
          <p>
            Choosing 'Separate' will keep the content separated by language per book.
          </p></span
        >
      </div>
    </li>
  {/if}
  <li class="bg-primary p-2">
    <div class="flex justify-between">
      <span class="text-neutral-content">Generate PDF</span>
      <input type="checkbox" bind:checked={$generatePdfStore} class="toggle" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will cause a PDF of the document to be generated.</span
      >
    </div>
  </li>
  <li class="bg-primary p-2">
    <div class="flex justify-between">
      <span class="text-neutral-content">Generate Epub</span>
      <input type="checkbox" bind:checked={$generateEpubStore} class="toggle" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will cause a ePub of the document to be generated.</span
      >
    </div>
  </li>
  <li class="bg-primary p-2">
    <div class="flex justify-between">
      <span class="text-neutral-content">Generate Docx</span>
      <input type="checkbox" bind:checked={$generateDocxStore} class="toggle" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will cause a Docx of the document to be generated.</span
      >
    </div>
  </li>
  <li class="bg-primary p-2">
    <div class="flex justify-between">
      <label for="email" class="text-neutral-content"
        >{import.meta.env.VITE_EMAIL_LABEL}</label
      >
      <input
        type="text"
        name="email"
        id="email"
        bind:value={$emailStore}
        placeholder="Type email address here (optional)"
        class="input input-bordered bg-primary w-full max-w-xs"
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
