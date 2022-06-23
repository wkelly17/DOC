<script lang="ts">
  import type { AssemblyStrategy } from '../types'

  let book_language_order_strategy: AssemblyStrategy = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let language_book_order_strategy: AssemblyStrategy = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let assemblyStrategies = [book_language_order_strategy, language_book_order_strategy]

  export let assemblyStrategy: AssemblyStrategy | null
</script>

<div>
  <h3>{import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER}</h3>
  <select bind:value={assemblyStrategy} name="assemblyStrategy">
    {#each assemblyStrategies as assemblyStrategy}
      <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option>
    {/each}
  </select>
</div>
