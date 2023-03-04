import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BoardModule } from "@mangoplace/board/board.module";
import { ModalModule } from "@mangoplace/modal/modal.module";
import { AppComponent } from "./app.component";

@NgModule({
	bootstrap: [AppComponent],
	declarations: [AppComponent],
	imports: [BoardModule, BrowserModule, CommonModule, ModalModule]
})
export class AppModule {}
