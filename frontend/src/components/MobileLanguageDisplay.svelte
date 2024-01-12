<script lang="ts">
  import { getCode, getName } from '../lib/utils'
  import {
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore,
    langCodesStore
  } from '../stores/LanguagesStore'

  export let showGatewayLanguages: boolean
  export let gatewayCodesAndNames: Array<string>
  export let heartCodesAndNames: Array<string>
  export let filteredGatewayCodeAndNames: Array<string>
  export let filteredHeartCodeAndNames: Array<string>
  export let maxLanguages: number
</script>

<main class="flex-1 overflow-y-auto p-4">
  {#if showGatewayLanguages}
    {#each gatewayCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="pl-4 py-2 target"
          style={filteredGatewayCodeAndNames.includes(langCodeAndName)
            ? ''
            : 'display: none'}
        >
          <div class="flex items-center justify-between target2">
            <div class="flex items-center target3">
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$gatewayCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
                disabled={$langCountStore == maxLanguages &&
                  !$langCodesStore.includes(getCode(langCodeAndName))}
              />
              <span class="text-[#33445C] text-xl pl-1">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-[#33445C] text-xl">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {:else}
    {#each heartCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="pl-4 py-2 target"
          style={filteredHeartCodeAndNames.includes(langCodeAndName)
            ? ''
            : 'display: none'}
        >
          <div class="flex items-center justify-between target2">
            <div class="flex items-center target3">
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$heartCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
                disabled={$langCountStore == maxLanguages &&
                  !$langCodesStore.includes(getCode(langCodeAndName))}
              />
              <span class="text-[#33445C] text-xl pl-1">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-[#33445C] text-xl">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {/if}
</main>
