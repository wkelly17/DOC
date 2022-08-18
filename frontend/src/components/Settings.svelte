<script lang="ts">
  import type { AssemblyStrategy } from '../types'
  import {
    printOptimizationStore,
    assemblyStrategyKindStore
  } from '../stores/SettingsStore'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'

  let book_language_order_strategy: AssemblyStrategy = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let language_book_order_strategy: AssemblyStrategy = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let assemblyStrategies = [book_language_order_strategy, language_book_order_strategy]

  // let assemblyStrategy: AssemblyStrategy | null
  const assemblyStrategyHeader = <string>import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER

  $: console.log(`$assemblyStrategyKindStore: ${$assemblyStrategyKindStore}`)
</script>

<h3 class="bg-white text-lg pb-8 pt-2 pl-2">Interleave Settings</h3>
<ul>
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="">Print Optimization</span>
      <input type="checkbox" class="toggle" checked />
    </div>
    <div>
      <span class="text-sm">Enabling this option will remove extra whitespace</span>
    </div>
  </li>
  {#if $lang1NameAndCode}
    <li class="bg-white p-2">
      <div class="flex justify-between">
        <span>{assemblyStrategyHeader}</span>
        <select bind:value={$assemblyStrategyKindStore} name="assemblyStrategy">
          {#each assemblyStrategies as assemblyStrategy}
            <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option>
          {/each}
        </select>
      </div>
      <div>
        <span class="text-sm"
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
</ul>

<div class="flex items-center justify-center h-28 bg-white">
  <button
    class="flex btn btn-disabled w-5/6 rounded"
    on:click={() => console.log('generate document...')}
  >
    <span class="text-xl py-2 px-4 text-gray-500 capitalize">Generate Document</span>
  </button>
</div>
