import type { InjectionKey } from "vue";

import type { UserRefAndSetter } from "@/arches_rascolls/Search/types.ts";

export const DEFAULT_ERROR_TOAST_LIFE = 8000;
export const ERROR = "error";
export const USER_KEY = Symbol() as InjectionKey<UserRefAndSetter>;
export const TERM_FILTER_TYPE = "term";
export const FACET_FILTER_TYPE = "facet";
