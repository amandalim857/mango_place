import { NgModule } from "@angular/core";
import { ModalBodyComponent } from "@mangoplace/modal/body/modalbody.component";
import { ModalFooterComponent } from "@mangoplace/modal/footer/modalfooter.component";
import { ModalComponent } from "./modal.component";

@NgModule({
	declarations: [ModalComponent, ModalBodyComponent, ModalFooterComponent],
	exports: [ModalComponent, ModalBodyComponent, ModalFooterComponent]
})
export class ModalModule {}
