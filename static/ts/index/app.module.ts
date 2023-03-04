import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BoardModule } from "@mangoplace/board/board.module";
import { BootstrapModule } from "@mangoplace/bootstrap/bootstrap.module";
import { AppComponent } from "./app.component";

@NgModule({
	bootstrap: [AppComponent],
	declarations: [AppComponent],
	imports: [BoardModule, BrowserModule, CommonModule, BootstrapModule]
})
export class AppModule {}
