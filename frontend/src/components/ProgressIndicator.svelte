<script lang="ts">
  import { onMount } from 'svelte'
  let text: string = ''
  export let labelString: string = 'Loading'
  export let parClass: string = ''

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

<p class={parClass}>{labelString}{text}</p>

<!-- Usage example: -->
<!-- <ProgressIndicator -->
<!--   parClass="text-center text-secondary-content" -->
<!--   labelString="Generating document" -->
<!-- /> -->
