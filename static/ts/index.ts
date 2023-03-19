import "zone.js";

import {platformBrowser} from "@angular/platform-browser";
import {AppModule} from "./index/app.module";

platformBrowser().bootstrapModule(AppModule);
