import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { VisionService, Prediction } from './vision.service';

describe('VisionService', () => {
  let service: VisionService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });

    service = TestBed.inject(VisionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  function createFile(): File {
    return new File([new Blob(['data'], { type: 'image/png' })], 'sample.png', { type: 'image/png' });
  }

  it('normalizes array-based predictions', () => {
    let result: Prediction[] | undefined;

    service.predict(createFile()).subscribe((res) => (result = res.predictions));

    const req = httpMock.expectOne('/vision/predict');
    expect(req.request.method).toBe('POST');

    req.flush({ predictions: [{ class: 'mango', score: 0.82 }] });

    expect(result).toEqual([{ class: 'mango', score: 0.82 }]);
  });

  it('coerces single fruit responses into predictions', () => {
    let result: Prediction[] | undefined;

    service.predict(createFile()).subscribe((res) => (result = res.predictions));

    const req = httpMock.expectOne('/vision/predict');
    expect(req.request.method).toBe('POST');

    req.flush({ fruit: 'banana', confidence: 0.65 });

    expect(result).toEqual([{ class: 'banana', score: 0.65 }]);
  });
});
