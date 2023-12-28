<script lang="ts">
  import { langCountStore } from '../stores/LanguagesStore'
  import Modal from './Modal.svelte'
  import ProgressIndicator from './ProgressIndicator.svelte'

  export let langCodeNameAndTypes: Array<[string, string, boolean]>
  export let showGatewayLanguages: boolean
  export let gatewaySearchTerm: string
  export let heartSearchTerm: string
  export let showFilterMenu: boolean
  export let showWizardBasketModal: boolean
</script>

<div class="flex items-center px-2 py-2 mt-2 bg-white">
  {#if !langCodeNameAndTypes || langCodeNameAndTypes.length === 0}
    <div class="ml-4">
      <ProgressIndicator />
    </div>
  {:else}
    <div class="flex items-center">
      {#if showGatewayLanguages}
        <label id="label-for-filter-gl-langs" for="filter-gl-langs">
          <input
            id="filter-gl-langs"
            bind:value={gatewaySearchTerm}
            placeholder="Search Languages"
            class="input input-bordered bg-white sm:w-full max-w-xs"
          />
        </label>
        <div class="ml-2 hidden sm:flex" role="group">
          <button
            class="rounded-l-md w-36 h-10 bg-[#015ad9] text-white font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9] transition duration-150 ease-in-out"
            on:click={() => (showGatewayLanguages = true)}
          >
            Gateway
          </button>
          <button
            class="rounded-r-md w-36 h-10 bg-white text-[#33445C] font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
            on:click={() => (showGatewayLanguages = false)}
          >
            Heart
          </button>
        </div>
        <div class="flex sm:hidden ml-2">
          <button on:click={() => (showFilterMenu = true)}>
            {#if showFilterMenu}
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <rect width="56" height="48" rx="12" fill="#001533" />
                <path
                  d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                  fill="white"
                />
              </svg>
            {:else}
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                  fill="#33445C"
                />
                <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
              </svg>
            {/if}
          </button>
          <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
            <div class="relative">
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
                  fill="#33445C"
                />
                <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
              </svg>
              {#if $langCountStore > 0}
                <!-- badge -->
                <div
                  class="text-center absolute -top-0.5 -right-0.5
                            bg-neutral-focus text-neutral-content
                            rounded-full w-7 h-7"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span class="text-[8px] text-white">{$langCountStore}</span>
                </div>
              {/if}
            </div>
          </button>
        </div>
        {#if showFilterMenu}
          <Modal
            title="Filter"
            open={showFilterMenu}
            on:close={() => (showFilterMenu = false)}
          >
            <svelte:fragment slot="body">
              <div class="flex items-center">
                <input
                  id="show-gateway-radio-button"
                  type="radio"
                  value={true}
                  bind:group={showGatewayLanguages}
                  class="radio checked:bg-[#015ad9]"
                />
                <label for="show-gateway-radio-button" class="text-[#33445C] pl-1"
                  >Gateway languages</label
                >
              </div>
              <div class="flex items-center">
                <input
                  id="show-heart-radio-button"
                  type="radio"
                  value={false}
                  bind:group={showGatewayLanguages}
                  class="radio checked:bg-[#015ad9]"
                />
                <label for="show-heart-radio-button" class="text-[#33445C] pl-1"
                  >Heart languages</label
                >
              </div>
            </svelte:fragment>
          </Modal>
        {/if}
      {:else}
        <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
          <input
            id="filter-non-gl-langs"
            bind:value={heartSearchTerm}
            placeholder="Search Languages"
            class="input input-bordered bg-white sm:w-full max-w-xs"
          />
        </label>
        <div class="ml-2 hidden sm:flex" role="group">
          <button
            class="rounded-l-md w-36 h-10 bg-white text-[#33445c] font-medium leading-tight border-x-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white transition duration-150 ease-in-out"
            on:click={() => (showGatewayLanguages = true)}
          >
            Gateway
          </button>
          <button
            class="rounded-r-md w-36 h-10 bg-[#015ad9]
                    text-white font-medium leading-tight border-r-2 border-t-2 border-b-2 border-[#015ad9] hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8] transition duration-150 ease-in-out"
            on:click={() => (showGatewayLanguages = false)}
          >
            Heart
          </button>
        </div>
        <div class="flex sm:hidden ml-2">
          <button on:click={() => (showFilterMenu = true)}>
            {#if showFilterMenu}
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <rect width="56" height="48" rx="12" fill="#001533" />
                <path
                  d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                  fill="white"
                />
              </svg>
            {:else}
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M38.125 19.875H17.875C17.5766 19.875 17.2905 19.7565 17.0795 19.5455C16.8685 19.3345 16.75 19.0484 16.75 18.75C16.75 18.4516 16.8685 18.1655 17.0795 17.9545C17.2905 17.7435 17.5766 17.625 17.875 17.625H38.125C38.4234 17.625 38.7095 17.7435 38.9205 17.9545C39.1315 18.1655 39.25 18.4516 39.25 18.75C39.25 19.0484 39.1315 19.3345 38.9205 19.5455C38.7095 19.7565 38.4234 19.875 38.125 19.875ZM34.375 25.125H21.625C21.3266 25.125 21.0405 25.0065 20.8295 24.7955C20.6185 24.5845 20.5 24.2984 20.5 24C20.5 23.7016 20.6185 23.4155 20.8295 23.2045C21.0405 22.9935 21.3266 22.875 21.625 22.875H34.375C34.6734 22.875 34.9595 22.9935 35.1705 23.2045C35.3815 23.4155 35.5 23.7016 35.5 24C35.5 24.2984 35.3815 24.5845 35.1705 24.7955C34.9595 25.0065 34.6734 25.125 34.375 25.125ZM29.875 30.375H26.125C25.8266 30.375 25.5405 30.2565 25.3295 30.0455C25.1185 29.8345 25 29.5484 25 29.25C25 28.9516 25.1185 28.6655 25.3295 28.4545C25.5405 28.2435 25.8266 28.125 26.125 28.125H29.875C30.1734 28.125 30.4595 28.2435 30.6705 28.4545C30.8815 28.6655 31 28.9516 31 29.25C31 29.5484 30.8815 29.8345 30.6705 30.0455C30.4595 30.2565 30.1734 30.375 29.875 30.375Z"
                  fill="#33445C"
                />
                <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
              </svg>
            {/if}
          </button>
          <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
            <div class="relative">
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
                  fill="#33445C"
                />
                <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
              </svg>
              {#if $langCountStore > 0}
                <!-- badge -->
                <div
                  class="text-center absolute -top-0.5 -right-0.5
                          bg-neutral-focus text-neutral-content
                          rounded-full w-7 h-7"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span class="text-[8px] text-white">{$langCountStore}</span>
                </div>
              {/if}
            </div>
          </button>
        </div>
        {#if showFilterMenu}
          <Modal
            title="Filter"
            open={showFilterMenu}
            on:close={() => (showFilterMenu = false)}
          >
            <svelte:fragment slot="body">
              <div class="flex items-center">
                <input
                  id="show-gateway-radio-button"
                  type="radio"
                  value={true}
                  bind:group={showGatewayLanguages}
                  class="radio checked:bg-[#015ad9]"
                />
                <label for="show-gateway-radio-button" class="text-[#33445C] pl-1"
                  >Gateway languages</label
                >
              </div>
              <div class="flex items-center">
                <input
                  id="show-heart-radio-button"
                  type="radio"
                  value={false}
                  bind:group={showGatewayLanguages}
                  class="radio checked:bg-[#015ad9]"
                />
                <label for="show-heart-radio-button" class="text-[#33445C] pl-1"
                  >Heart languages</label
                >
              </div>
            </svelte:fragment>
          </Modal>
        {/if}
      {/if}
    </div>
  {/if}
</div>
