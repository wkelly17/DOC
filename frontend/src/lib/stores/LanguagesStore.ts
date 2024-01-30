import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

export let lang0NameAndCodeStore: Writable<string> = writable('');
export let lang1NameAndCodeStore: Writable<string> = writable('');
export let langCodesStore: Writable<Array<string>> = writable([]);
export let langNamesStore: Writable<Array<string>> = writable([]);
export let langCountStore: Writable<number> = writable<number>(0);

export let gatewayCodeAndNamesStore: Writable<Array<string>> = writable([]);
export let heartCodeAndNamesStore: Writable<Array<string>> = writable([]);
