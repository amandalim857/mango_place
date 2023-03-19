import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { ModalModule } from "@mangoplace/modal/modal.module";
import { AppComponent } from "./app.component";

@NgModule({
	bootstrap: [AppComponent],
	declarations: [AppComponent],
	imports: [BrowserModule, CommonModule, ModalModule]
})
export class AppModule {}
