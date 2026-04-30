sed -i '249,258c\
                {#if loading \&\& articles.length === 0}\
                        <div class="flex h-full flex-col gap-4 px-3.5 sm:px-4 py-2">\
                                {#each [1, 2, 3, 4, 5] as _}\
                                        <div class={`h-40 w-full animate-pulse rounded-xl ${dark ? "bg-white/5" : "bg-black/5"}`}></div>\
                                {/each}\
                        </div>\
