import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { BoardControlsComponent } from "@mangoplace/board/controls/boardcontrols.component";
import { BoardControlButtonComponent } from "@mangoplace/board/controls/button/boardcontrolbutton.component";
import { BoardToastContainerComponent } from "@mangoplace/board/toastcontainer/boardtoastcontainer.component";
import { BootstrapModule } from "@mangoplace/bootstrap/bootstrap.module";
import { BoardComponent } from "./board.component";

@NgModule({
	declarations: [
		BoardComponent,
		BoardControlButtonComponent,
		BoardControlsComponent,
		BoardToastContainerComponent
	],

	exports: [BoardComponent],
	imports: [CommonModule, BootstrapModule],
})
export class BoardModule {}
