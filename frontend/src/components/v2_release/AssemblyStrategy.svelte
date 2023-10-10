<script lang="ts">

  import { settingsUpdated } from '../../stores/v2_release/SettingsStore'
  import type { SelectElement } from '../../types'

  let bookLanguageOrderStrategy: SelectElement = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let languageBookOrderStrategy: SelectElement = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let assemblyStrategies = [bookLanguageOrderStrategy, languageBookOrderStrategy]

  export let assemblyStrategy: SelectElement | null
</script>

<div>
  <h3>{import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER}</h3>
  <select bind:value={assemblyStrategy} name="assemblyStrategy"
          on:change={() => ($settingsUpdated = true)}>
    {#each assemblyStrategies as assemblyStrategy}
      <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option>
    {/each}
  </select>
</div>
