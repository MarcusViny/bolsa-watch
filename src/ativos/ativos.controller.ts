import { Controller, Get, Query } from '@nestjs/common';
import { AtivosService, Ativo } from './ativos.service';

@Controller('ativos')
export class AtivosController {
  constructor(private readonly ativosService: AtivosService) {}

  @Get()
  async listar(@Query('ticker') ticker?: string): Promise<Ativo[] | Ativo> {
    if (ticker) {
      return this.ativosService.buscarPorTicker(ticker);
    }
    return this.ativosService.buscarTodos();
  }
}
