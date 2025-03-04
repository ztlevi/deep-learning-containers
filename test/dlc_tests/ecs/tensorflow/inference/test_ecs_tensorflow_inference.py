import pytest

import test.test_utils.ecs as ecs_utils
import test.test_utils.ec2 as ec2_utils
from test.test_utils import (
    get_tensorflow_model_name,
    request_tensorflow_inference,
    request_tensorflow_inference_nlp,
    is_nightly_context,
)
from test.test_utils import (
    ECS_AML2_CPU_USWEST2,
    ECS_AML2_GPU_USWEST2,
    ECS_AML2_NEURON_USWEST2,
    ECS_AML2_GRAVITON_CPU_USWEST2,
)


@pytest.mark.model("half_plus_two")
@pytest.mark.team("frameworks")
@pytest.mark.parametrize("ecs_instance_type", ["c5.4xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_CPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_cpu(
    tensorflow_inference, ecs_container_instance, region, cpu_only
):
    __ecs_tensorflow_inference_cpu(tensorflow_inference, ecs_container_instance, region)


@pytest.mark.model("half_plus_two")
@pytest.mark.parametrize("ecs_instance_type", ["c6g.4xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_GRAVITON_CPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_graviton_cpu(
    tensorflow_inference_graviton, ecs_container_instance, region, cpu_only
):
    __ecs_tensorflow_inference_cpu(tensorflow_inference_graviton, ecs_container_instance, region)


def __ecs_tensorflow_inference_cpu(tensorflow_inference, ecs_container_instance, region):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)

    model_name = "saved_model_half_plus_two"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            region=region,
        )
        model_name = get_tensorflow_model_name("cpu", model_name)
        inference_result = request_tensorflow_inference(model_name, ip_address=public_ip_address)
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.integration("elastic_inference")
@pytest.mark.model("half_plus_two")
@pytest.mark.parametrize("ecs_instance_type", ["c5.4xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_CPU_USWEST2], indirect=True)
@pytest.mark.parametrize("ei_accelerator_type", ["eia1.large"], indirect=True)
def test_ecs_tensorflow_inference_eia(
    tensorflow_inference_eia, ecs_container_instance, ei_accelerator_type, region
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)

    model_name = "saved_model_half_plus_two"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference_eia,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            ei_accelerator_type,
            region=region,
        )
        model_name = get_tensorflow_model_name("eia", model_name)
        inference_result = request_tensorflow_inference(model_name, ip_address=public_ip_address)
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.model("simple")
@pytest.mark.parametrize("ecs_instance_type", ["inf1.2xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_NEURON_USWEST2], indirect=True)
@pytest.mark.team("neuron")
def test_ecs_tensorflow_inference_neuron(
    tensorflow_inference_neuron, ecs_container_instance, region
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)
    num_neurons = ec2_utils.get_instance_num_inferentias(worker_instance_id)

    model_name = "simple"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference_neuron,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            num_neurons=num_neurons,
            region=region,
        )
        model_name = get_tensorflow_model_name("neuron", model_name)
        inference_result = request_tensorflow_inference(
            model_name,
            ip_address=public_ip_address,
            inference_string="'{\"instances\": [[1.0, 2.0, 5.0]]}'",
        )
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.model("simple")
@pytest.mark.parametrize("ecs_instance_type", ["trn1.2xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_NEURON_USWEST2], indirect=True)
@pytest.mark.team("neuron")
def test_ecs_tensorflow_inference_neuronx(
    tensorflow_inference_neuronx, ecs_container_instance, region
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)
    num_neurons = 1

    model_name = "simple"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference_neuronx,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            num_neurons=num_neurons,
            region=region,
        )
        model_name = get_tensorflow_model_name("neuronx", model_name)
        inference_result = request_tensorflow_inference(
            model_name,
            ip_address=public_ip_address,
            inference_string="'{\"instances\": [[1.0, 2.0, 5.0]]}'",
        )
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.model("simple")
@pytest.mark.parametrize("ecs_instance_type", ["inf2.xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_NEURON_USWEST2], indirect=True)
@pytest.mark.team("neuron")
def test_ecs_tensorflow_inference_neuronx_inf2(
    tensorflow_inference_neuronx, ecs_container_instance, region
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)
    num_neurons = 1

    model_name = "simple"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference_neuronx,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            num_neurons=num_neurons,
            region=region,
        )
        model_name = get_tensorflow_model_name("neuronx", model_name)
        inference_result = request_tensorflow_inference(
            model_name,
            ip_address=public_ip_address,
            inference_string="'{\"instances\": [[1.0, 2.0, 5.0]]}'",
        )
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.model("half_plus_two")
@pytest.mark.team("frameworks")
@pytest.mark.parametrize("ecs_instance_type", ["g4dn.8xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_GPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_gpu(
    tensorflow_inference, ecs_container_instance, region, gpu_only
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)
    num_gpus = ec2_utils.get_instance_num_gpus(worker_instance_id)

    model_name = "saved_model_half_plus_two"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            num_gpus=num_gpus,
            region=region,
        )
        model_name = get_tensorflow_model_name("gpu", model_name)
        inference_result = request_tensorflow_inference(model_name, ip_address=public_ip_address)
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.skipif(
    not is_nightly_context(), reason="Running additional model in nightly context only"
)
@pytest.mark.model("albert")
@pytest.mark.team("frameworks")
@pytest.mark.parametrize("ecs_instance_type", ["c5.4xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_CPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_cpu_nlp(
    tensorflow_inference, ecs_container_instance, region, cpu_only
):
    __ecs_tensorflow_inference_cpu_nlp(tensorflow_inference, ecs_container_instance, region)


# @pytest.mark.skipif(not is_nightly_context(), reason="Running additional model in nightly context only")
@pytest.mark.model("albert")
@pytest.mark.parametrize("ecs_instance_type", ["c6g.4xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_GRAVITON_CPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_graviton_cpu_nlp(
    tensorflow_inference_graviton, ecs_container_instance, region, cpu_only
):
    __ecs_tensorflow_inference_cpu_nlp(
        tensorflow_inference_graviton, ecs_container_instance, region
    )


def __ecs_tensorflow_inference_cpu_nlp(tensorflow_inference, ecs_container_instance, region):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)

    model_name = "albert"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            region=region,
        )
        model_name = get_tensorflow_model_name("cpu", model_name)
        inference_result = request_tensorflow_inference_nlp(
            model_name, ip_address=public_ip_address
        )
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )


@pytest.mark.skipif(
    not is_nightly_context(), reason="Running additional model in nightly context only"
)
@pytest.mark.model("albert")
@pytest.mark.team("frameworks")
@pytest.mark.parametrize("ecs_instance_type", ["g4dn.8xlarge"], indirect=True)
@pytest.mark.parametrize("ecs_ami", [ECS_AML2_GPU_USWEST2], indirect=True)
def test_ecs_tensorflow_inference_gpu_nlp(
    tensorflow_inference, ecs_container_instance, region, gpu_only
):
    worker_instance_id, ecs_cluster_arn = ecs_container_instance
    public_ip_address = ec2_utils.get_public_ip(worker_instance_id, region=region)
    num_gpus = ec2_utils.get_instance_num_gpus(worker_instance_id)

    model_name = "albert"
    service_name = task_family = revision = None
    try:
        service_name, task_family, revision = ecs_utils.setup_ecs_inference_service(
            tensorflow_inference,
            "tensorflow",
            ecs_cluster_arn,
            model_name,
            worker_instance_id,
            num_gpus=num_gpus,
            region=region,
        )
        model_name = get_tensorflow_model_name("gpu", model_name)
        inference_result = request_tensorflow_inference_nlp(
            model_name, ip_address=public_ip_address
        )
        assert inference_result, f"Failed to perform inference at IP address: {public_ip_address}"

    finally:
        ecs_utils.tear_down_ecs_inference_service(
            ecs_cluster_arn, service_name, task_family, revision
        )
