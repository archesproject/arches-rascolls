import type { InjectionKey } from "vue";

import type { UserRefAndSetter } from "@/afrc/Search/types.ts";

export const DEFAULT_ERROR_TOAST_LIFE = 8000;
export const ERROR = "error";
export const USER_KEY = Symbol() as InjectionKey<UserRefAndSetter>;
