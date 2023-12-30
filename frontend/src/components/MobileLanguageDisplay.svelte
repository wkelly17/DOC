<script lang="ts">
  import { getCode, getName } from '../lib/utils'
  import {
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore
  } from '../stores/LanguagesStore'

  export let showGatewayLanguages: boolean
  export let gatewayCodesAndNames: Array<string>
  export let heartCodesAndNames: Array<string>
  export let filteredGatewayCodeAndNames: Array<string>
  export let filteredHeartCodeAndNames: Array<string>

  const maxLanguages = 2
</script>

<main class="flex-1 overflow-y-auto p-4">
  {#if showGatewayLanguages}
    {#each gatewayCodesAndNames as langCodeAndName, index}
      <div class="pl-4 py-2 target">
        <div
          class="flex items-center justify-between target2"
          style={filteredGatewayCodeAndNames.includes(langCodeAndName)
            ? ''
            : 'display: none'}
        >
          <div class="flex items-center target3">
            <input
              id="lang-code-{index}"
              type="checkbox"
              bind:group={$gatewayCodeAndNamesStore}
              value={langCodeAndName}
              class="checkbox checkbox-dark-bordered"
            />
            <label for="lang-code-{index}" class="text-[#33445C] pl-1"
              >{getName(langCodeAndName)}</label
            >
          </div>
        </div>
        <div class="ml-6 text-[#33445C]">{getCode(langCodeAndName)}</div>
      </div>
    {/each}
  {:else}
    {#each heartCodesAndNames as langCodeAndName, index}
      <div class="pl-4 py-2 target">
        <div
          class="flex items-center justify-between target2"
          style={filteredHeartCodeAndNames.includes(langCodeAndName)
            ? ''
            : 'display: none'}
        >
          <div class="flex items-center target3">
            <input
              id="lang-code-{index}"
              type="checkbox"
              bind:group={$heartCodeAndNamesStore}
              value={langCodeAndName}
              class="checkbox checkbox-dark-bordered"
            />
            <label for="lang-code-{index}" class="text-[#33445C] pl-1"
              >{getName(langCodeAndName)}</label
            >
          </div>
        </div>
        <div class="ml-6 text-[#33445C]">{getCode(langCodeAndName)}</div>
      </div>
    {/each}
  {/if}
  {#if $langCountStore > maxLanguages}
    <div class="toast toast-center toast-middle">
      <div class="alert alert-error">
        <div>
          <span
            >You've selected more than two languages, please choose up to two languages.</span
          >
        </div>
      </div>
    </div>
  {/if}
</main>
