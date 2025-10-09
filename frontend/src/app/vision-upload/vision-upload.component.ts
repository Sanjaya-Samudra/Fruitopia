import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { VisionService } from '../services/vision.service';

@Component({
  selector: 'app-vision-upload',
  templateUrl: './vision-upload.component.html',
  styleUrls: ['./vision-upload.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatProgressSpinnerModule, MatSnackBarModule, MatIconModule],
})
export class VisionUploadComponent {
  file?: File;
  preview?: string | ArrayBuffer | null;
  predictions: any[] = [];
  loading = false;
  lowConfidence = false;

  constructor(private vision: VisionService, private snack: MatSnackBar) {}

  onFile(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const f = input.files[0];
    // basic MIME-type validation
    if (!f.type.startsWith('image/')) {
      this.snack.open('Please upload an image file (jpg, png, jpeg)', 'Close', { duration: 3500 });
      input.value = '';
      return;
    }
    this.file = f;
    const reader = new FileReader();
    reader.onload = () => (this.preview = reader.result);
    reader.readAsDataURL(this.file);
  }

  upload() {
    if (!this.file) return;
    this.loading = true;
    this.vision.predict(this.file).subscribe({
      next: (res) => {
        this.predictions = res.predictions || [];
        this.lowConfidence = false;
        if (this.predictions.length) {
          const top = this.predictions[0];
          // if model isn't confident, treat as non-fruit
          if (!top || top.score < 0.45) {
            this.lowConfidence = true;
            this.predictions = [];
          }
        }
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
        this.snack.open('Prediction failed — check console', 'Close', { duration: 4000 });
      },
    });
  }
}
