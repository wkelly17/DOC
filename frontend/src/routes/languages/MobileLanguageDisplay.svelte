<script lang="ts">
  import { PUBLIC_MAX_LANGUAGES } from '$env/static/public'
  import { getCode, getName } from '$lib/utils'
  import {
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore,
    langCodesStore
  } from '$lib/stores/LanguagesStore'

  export let showGatewayLanguages: boolean
  export let gatewayCodesAndNames: Array<string>
  export let heartCodesAndNames: Array<string>
  export let filteredGatewayCodeAndNames: Array<string>
  export let filteredHeartCodeAndNames: Array<string>
  let maxLanguages: number = PUBLIC_MAX_LANGUAGES as unknown as number
</script>

<main class="flex-1 overflow-y-auto p-4">
  {#if showGatewayLanguages}
    {#each gatewayCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="target py-2 pl-4"
          style={filteredGatewayCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
        >
          <div class="target2 flex items-center justify-between">
            <div class="target3 flex items-center">
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$gatewayCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
                disabled={$langCountStore == maxLanguages &&
                  !$langCodesStore.includes(getCode(langCodeAndName))}
              />
              <span class="pl-1 text-xl text-[#33445C]">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-xl text-[#33445C]">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {:else}
    {#each heartCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="target py-2 pl-4"
          style={filteredHeartCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
        >
          <div class="target2 flex items-center justify-between">
            <div class="target3 flex items-center">
              <input
                id="lang-code-{index}"
                type="checkbox"
                bind:group={$heartCodeAndNamesStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
                disabled={$langCountStore == maxLanguages &&
                  !$langCodesStore.includes(getCode(langCodeAndName))}
              />
              <span class="pl-1 text-xl text-[#33445C]">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-xl text-[#33445C]">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {/if}
</main>
