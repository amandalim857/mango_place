import { NgModule } from "@angular/core";
import { ModalComponent } from "@mangoplace/bootstrap/modal/modal.component";
import { ModalBodyComponent } from "@mangoplace/bootstrap/modal/body/modalbody.component";
import { ModalFooterComponent } from "@mangoplace/bootstrap/modal/footer/modalfooter.component";
import { TooltipDirective } from "@mangoplace/bootstrap/tooltip/tooltip.directive";

@NgModule({
	declarations: [ModalComponent, ModalBodyComponent, ModalFooterComponent, TooltipDirective],
	exports: [ModalComponent, ModalBodyComponent, ModalFooterComponent, TooltipDirective]
})
export class BootstrapModule {}
