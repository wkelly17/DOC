<script lang="ts">
  import type { AssemblyStrategy } from '../types'
  import Select, { Option } from '@smui/select'

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
  <Select bind:value={assemblyStrategy} label="Choose assembly">
    {#each assemblyStrategies as assemblyStrategy}
      <Option value={assemblyStrategy.id}>{assemblyStrategy.label}</Option>
    {/each}
  </Select>
  <!-- <select bind:value={assemblyStrategy} name="assemblyStrategy"> -->
  <!--   {#each assemblyStrategies as assemblyStrategy} -->
  <!--     <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option> -->
  <!--   {/each} -->
  <!-- </select> -->
</div>
