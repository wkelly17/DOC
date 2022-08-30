<script lang="ts">
  import { onMount } from 'svelte'
  let text: string = ''
  export let labelString: string = 'Loading'
  export let parClass: string = ''
  export let graphicStyle: boolean = false
  let graphicClassDefault: string = 'progress'
  export let graphicClass: string = 'w-56'
  let graphicClasses: string = `${graphicClassDefault} ${graphicClass}`
  export let graphicValue: string = '30'
  export let graphicMax: string = '100'

  async function loop() {
    if (text.length === 3) text = ''
    text += '.'
    await new Promise(resolve => setTimeout(resolve, 300))
    loop()
  }

  onMount(() => {
    loop()
  })
</script>

{#if graphicStyle}
  <progress class={graphicClasses} value={graphicValue} max={graphicMax} />
{:else}
  <p class={parClass}>{labelString}{text}</p>
{/if}
